from med_assist_app.modules.user_management import create_connection,save_appointment,check_parameters_filled,init_session_state, create_user_profiles_table, change_user_role, save_user_profile, save_user_result, save_user_role, get_user_profile, get_age_of_user, get_height_of_user, get_result_of_user, get_sex_of_user, get_kilo_of_user, get_pregnancies_of_user, get_user_role, get_user_appointments, findWholeWord, extract_text_from_pdf
from med_assist_app.modules.appointments import create_appointed_hours_table
from med_assist_app.modules.doctor import create_doctor_table,get_day_of_week,save_doc_info,get_available_hours,get_doctors_by_specialty_and_city,get_doctor_profile,get_available_hours_excluding_booked,get_doctor_appointments,create_doctor_schedule_table,set_default_schedule,set_default_schedule_av_hours,save_doctor_schedule,get_doctor_schedule
import pickle
import requests
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_login_auth_ui.widgets import __login__
from streamlit_login_auth_ui.utils import register_new_usr
import re
from io import BytesIO
import pandas as pd
from datetime import timedelta, datetime
from datetime import datetime as dt
from streamlit_calendar import calendar

if 'selected_hour' not in st.session_state:
    st.session_state.selected_hour = None
conn = create_connection()
create_user_profiles_table(conn)
create_doctor_table()
create_doctor_schedule_table()
init_session_state()
url = 'https://github.com/MagDaneca/MedAssist1/raw/main/MedAssist/Trained%20models/diabetes_model_medassist.sav'
response = requests.get(url)
if response.status_code == 200:
    with open('diabetes_model_medassist.sav', 'wb') as f:
        f.write(response.content)
    with open('diabetes_model_medassist.sav', 'rb') as f:
        diabetes_model = pickle.load(f)
else:
    print("Failed to download the model file")
doctors_in_plovdiv_cardiology = get_doctors_by_specialty_and_city('Cardiology', 'Plovdiv')
__login__obj = __login__(auth_token = "dk_test_R8RWEVDDQK4VYKH5FSXHTRZ5HK4E", 
                    company_name = "MedAssist",
                    width = 200, height = 250, 
                    logout_button_name = 'Logout', hide_menu_bool = False, 
                    hide_footer_bool = False, 
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN = __login__obj.build_login_ui()

extracted_text = ""
if 'Glucose' not in st.session_state:
    st.session_state.Glucose = None
if 'BloodPressure' not in st.session_state:
    st.session_state.BloodPressure = None
if 'Insulin' not in st.session_state:
    st.session_state.Insulin = None
if LOGGED_IN == True:
    username = __login__obj.cookies['__streamlit_login_signup_ui_username__']
    role_user = get_user_role(conn,username)
    if role_user is None:
        if username == 'admin':
            role_user = 'admin'
        else:
            role_user = 'user'
    save_user_role(conn,username,role_user)
    if role_user == 'user':
        with st.sidebar:
            selected = option_menu('MedAssist',
                            
                            [
                                'Профил',
                                'Запиши си час онлайн',
                                'Вашите записани часове',
                                'Диабет'
                            ],
                            icons=['person','activity','bandaid','heart'],
                            default_index=0)
        if(selected == 'Профил'):
            st.title("Вашият Профил")
            output = '1'
            age = get_age_of_user(conn, username)
            height = get_height_of_user(conn, username)
            sex = get_sex_of_user(conn, username)
            kilo = get_kilo_of_user(conn, username)
            pregnancies = get_pregnancies_of_user(conn, username)
            result = get_result_of_user(conn,username)
            if height != None:
                bmi = kilo/(height*height)
            if age:
                st.write(f"Възраст: {age} г.")
                st.write(f"Височина: {height} м.")
                st.write(f"Пол: {sex}")
                if sex == "жена":
                    st.write(f"Бременности: {pregnancies}")
                st.write(f"Тегло: {kilo} кг.")
                BMI = height/(kilo*kilo)
                if st.button("Променете вашите данни"):
                    age = None
                    result = None
                    save_user_profile(conn, username ,age,sex,pregnancies,height,kilo,result,role_user)
                    st.rerun()
            else:
                result = None
                Age = st.number_input("Възраст",1,100,None,1)
                Sex = st.radio("Пол",["мъж","жена"])
                if Sex=="мъж":
                    Pregnancies = 0
                else:
                    Pregnancies = st.text_input("Бременности" , placeholder = 'Брой бременности')
                Height = st.number_input("Височина",0.01,300.00,None,0.01, placeholder="Височината ви в метри(Пример 181см->1.81)")
                Kilo = st.number_input("Тегло", 0.01, 300.00,None, 0.01 , placeholder="Теглото ви в килограми")
                if height != None:
                    BMI = kilo/(height*height)
                if st.button("Запази") == True:
                    auth_par_check = check_parameters_filled(Age,Sex,Height,Kilo)
                    if auth_par_check == False:
                        st.error("Въведете вашите данни във всички полета!")
                    else:
                        save_user_profile(conn, username ,Age,Sex,Pregnancies,Height,Kilo,result,role_user)
                        conn.commit()
                        user_profile = get_user_profile(conn, username)
                        data_created = True
                        st.rerun()
            medical_tests = st.file_uploader("Качете вашите изследвания в PDF формат тук:", type=['pdf'])
            if medical_tests is not None:
                extracted_text = extract_text_from_pdf(BytesIO(medical_tests.read()))
            if findWholeWord('Глюкоза')(extracted_text) is not None:
                glucose_match = re.search(r'Глюкоза: (\d+)', extracted_text)
                Glucose = int(glucose_match.group(1)) if glucose_match else None
                st.session_state.Glucose = Glucose
            if findWholeWord('Кръвно')(extracted_text) is not None:
                pressure_match = re.search(r'Кръвно налягане: (\d+)', extracted_text)
                BloodPressure = int(pressure_match.group(1)) if pressure_match else None
                st.session_state.BloodPressure = BloodPressure
            if findWholeWord('Инсулин')(extracted_text) is not None:
                insulin_match = re.search(r'Инсулин: (\d+)', extracted_text)
                Insulin = int(insulin_match.group(1)) if insulin_match else None
                st.session_state.Insulin = Insulin
        if selected == 'Диабет':
                age = get_age_of_user(conn, username)
                height = get_height_of_user(conn, username)
                sex = get_sex_of_user(conn, username)
                kilo = get_kilo_of_user(conn, username)
                pregnancies = get_pregnancies_of_user(conn, username)
                result = get_result_of_user(conn,username)
                if height != None:
                    bmi = kilo/(height*height)
                if st.session_state.Glucose is not None:
                    Glucose = st.session_state.Glucose
                    output = 1
                else:
                    Glucose = None
                    print(Glucose)
                if st.session_state.BloodPressure is not None:
                    BloodPressure = st.session_state.BloodPressure
                    output = 1
                if st.session_state.Insulin is not None:
                    Insulin = st.session_state.Insulin
                    output = 1
                
                output = 1
                col1, col2, col3  = st.columns([1,1,1])
                col4,col5,col6 = st.columns([0.3,0.8,0.4])
                col7,col8 = st.columns([1.6,0.1])
                col9, col10, col11 = st.columns([1,1,1])
                col12,col13 = st.columns([1.6,0.1])
                with col1:
                    pass
                with col3:
                    pass
                with col2:
                    st.markdown("<h1 style=' color: black;'> " "Диабет</h1>", unsafe_allow_html=True)
                    with col7:
                        st.markdown("<b style='text-align: justify;color:black;text-decoration-style: solid;'>Диабетът е сериозно заболяване, което може да оказва значително влияние върху живота на хората. Неконтролираният диабет може да има дългосрочни последици за здравето, но разбирането на типовете диабет и начините за управление може да направи голяма разлика.</b>", unsafe_allow_html=True)
                        st.markdown("<h2 style=' color: black;text-align: center;'> " "Тип 1 Диабет</h1>", unsafe_allow_html=True)
                        st.markdown("<b style='text-align: justify;color:black;text-decoration-style: solid;'>Тип 1 диабет обикновено се развива при по-млади хора и е свързан с недостатъчно произвеждане на инсулин от тялото. Инсулинът е ключов хормон, който регулира нивата на захар в кръвта. Хората с този тип диабет обикновено се нуждаят от външен източник на инсулин, като инсулинови инжекции или помпи, за да контролират нивата на глюкоза.</b>", unsafe_allow_html=True)
                        st.markdown("<h2 style=' color: black;text-align: center;'> " "Тип 2 Диабет</h1>", unsafe_allow_html=True)
                        st.markdown("<b style='text-align: justify;color:black;text-decoration-style: solid;'>Тип 2 диабет е по-често срещан и обикновено се развива по-късно в живота. Тук тялото не използва инсулина ефективно или не произвежда достатъчно. Здравословен начин на живот, като здравословно хранене и редовна физическа активност, често помагат за контролиране на този вид диабет. В случаи, когато тези мерки не са достатъчни, могат да се използват и лекарства.</b>", unsafe_allow_html=True)
                        st.markdown("<h2 style=' color: black;text-align: center;'> " "Управление и Превенция</h1>", unsafe_allow_html=True)
                        st.markdown("<b style='text-align: justify;color:black;text-decoration-style: solid;'>Редовното следене на нивата на глюкоза в кръвта е от изключително значение за контролирането на диабета. Това включва редовни изследвания и следене на хранителните навици, физическата активност и приема на лекарства.</b>", unsafe_allow_html=True)
                        st.markdown("<b style='text-align: justify;color:black;text-decoration-style: solid;'>Важно е и предпазването от развитието на диабет. Здравословният начин на живот, включително балансирано хранене, поддържане на оптимално тегло и редовна физическа активност, може да намали риска от появата на диабет тип 2.</b>", unsafe_allow_html=True)
                        st.markdown("<b style='text-align: justify;color:black;text-decoration-style: solid;'>Диабетът е хронично заболяване, но разбирането му и вземането на мерки за контрол могат да помогнат за подобряване на качеството на живот и предотвратяване на дългосрочни здравни проблеми.</b>", unsafe_allow_html=True)
                    with col10:
                        if st.button("Резултат за диабет"):
                            if Glucose is None:
                                with col12:
                                    st.markdown("<p style='text-align: center; color: #F75D59;background-color:white;border-radius:25px;border: 2px solid #F75D59   ;'>Моля прикачете вашите изследвания в PDF формат в секция Профил</p>", unsafe_allow_html=True)
                            else:
                                try:
                                    if diabetes_model is not None:
                                        diab_prediction = diabetes_model.predict([[pregnancies, Glucose, BloodPressure, Insulin, bmi, age]])
                                        print(BloodPressure)
                                        print(Glucose)
                                        if (diab_prediction[0] == 1):
                                            diab_diagnosis = 'Пациентът е възможно да страда от диабет'
                                            output = '0'   
                                        else:
                                            diab_diagnosis = 'Пациентът не страда от диабет'
                                            output = '2'  
                                    else:
                                        st.write("Diabetes model is not loaded correctly.")
                                except Exception as e:
                                    print("Error during prediction:", e)
                                
                    
                    with col12:
                        if(output == '0'):
                            with col12:
                                st.markdown("<p style='text-align: center; color: #F75D59;background-color:white;border-radius:25px;border: 2px solid #F75D59   ;'>Пациентът е възможно да страда от диабет</p>", unsafe_allow_html=True)
                        elif(output == '2'):
                            with col12:
                                st.markdown("<p style='text-align: center; color: #F75D59;background-color:white;border-radius:25px;border: 2px solid #F75D59   ;'>Пациентът не страда от диабет</p>", unsafe_allow_html=True)
                    user_result = get_result_of_user(conn, username)
                    oblast = None
                    if user_result == 1:
                        online_chas = st.link_button("Запишете си час онлайн", '"http://localhost/edoc-doctor-appointment-system-main/"')
        if selected == 'Запиши си час онлайн':
                st.title('Намерете лекар и запазете час за преглед')
                selected_city = st.selectbox('Изберете град', ['Sofia', 'Plovdiv','Burgas','Varna'])
                selected_specialty = st.selectbox('Изберете специалност', ['Cardiology', 'Dermatology',])
                filtered = False
                if selected_city == "Plovdiv" and selected_specialty == "Cardiology":
                    doctors_in_plovdiv_cardiology = get_doctors_by_specialty_and_city('Cardiology', 'Plovdiv')
                    filtered = True
                if selected_city == "Sofia" and selected_specialty == "Cardiology":
                    doctors_in_sofia_cardiology = get_doctors_by_specialty_and_city('Cardiology', 'Sofia')
                    filtered = True
                if selected_city == "Burgas" and selected_specialty == "Cardiology":
                    doctors_in_burgas_cardiology = get_doctors_by_specialty_and_city('Cardiology', 'Burgas')
                    filtered = True
                if selected_city == "Varna" and selected_specialty == "Cardiology":
                    doctors_in_varna_cardiology = get_doctors_by_specialty_and_city('Cardiology', 'Varna')
                    filtered = True
                if not filtered:
                    st.write('Не бяха намерени доктори от тази специалност в града')
                else:
                    if selected_specialty == "Cardiology":
                        if selected_city == "Plovdiv":
                            doctors = get_doctors_by_specialty_and_city('Cardiology', 'Plovdiv')
                        elif selected_city == "Sofia":
                            doctors = get_doctors_by_specialty_and_city('Cardiology', 'Sofia')
                        elif selected_city == "Burgas":
                            doctors = get_doctors_by_specialty_and_city('Cardiology','Burgas')
                        elif selected_city == "Varna":
                            doctors = get_doctors_by_specialty_and_city('Cardiology','Varna')
                        else:
                            st.write('Градът не е избран или не са налични доктори от избраната специалност за този град.')

                    if doctors:
                        formatted_names = ['Dr. ' + doctor[0] + ' ' + doctor[1] for doctor in doctors]
                        selected_doctor = st.selectbox('Изберете лекар:', formatted_names)
                        if selected_doctor:
                            selected_index = formatted_names.index(selected_doctor)
                            print(selected_index)
                            selected_doctor_info = doctors_in_plovdiv_cardiology[selected_index]
                            doc_username = "doc_" + selected_doctor_info[0] 
                            selected_date = st.date_input('Select a date')
                            if selected_date:
                                sd = selected_date
                                selected_day = get_day_of_week(str(selected_date))
                            available_hours = get_available_hours(doc_username, selected_day)
                            if available_hours:
                                st.write(f"Available hours for {selected_doctor} on {selected_day}:")
                                num_rows = (len(available_hours) + 2) // 3
                                for i in range(num_rows):
                                    row_hours = available_hours[i * 3: (i + 1) * 3] 
                                    columns = st.columns(3)
                                    for j, hour in enumerate(row_hours):
                                        if st.session_state.selected_hour == hour:
                                            columns[j].button(hour, key=hour, help="color:red;")
                                        else:
                                            if columns[j].button(hour, key=hour):
                                                st.session_state.selected_hour = hour
                                    if i == (num_rows - 1):
                                        if columns[1].button("Запази час"):
                                            if st.session_state.selected_hour:
                                                save_appointment(doc_username, username, str(selected_date), st.session_state.selected_hour)
                                                available_hours = get_available_hours_excluding_booked(doc_username, selected_day)
                                                st.success(f"{username} вие записахте вашият час при {selected_doctor}, вашият час е от {st.session_state.selected_hour} на {sd}")
                            else:
                                st.write(f"Няма свободни часове при {selected_doctor} на {selected_day}")
                    else:
                        st.write('Градът не е избран или не са налични доктори от избраната специалност за този град.')
        if selected == 'Вашите записани часове':
                st.header("Това е вашият график за следния месец")
                user_appointments = get_user_appointments(username)
                if user_appointments:
                    appointments_for_calendar = [] 
                    for appointment in user_appointments:
                        doctor_username, appointment_date, appointment_hour = appointment
                        appointments_for_calendar.append(
                            {
                                "doctor_username": doctor_username,
                                "appointment_date": appointment_date,
                                "appointment_hour": appointment_hour,
                            }
                        )
                    events = []
                    for appointment in appointments_for_calendar:
                        event = {
                            "title": appointment["doctor_username"],
                            "color": "#FF4B4B",  # Red color
                            "start": f"{appointment['appointment_date']}T{appointment['appointment_hour']}",
                            "end": f"{appointment['appointment_date']}T{appointment['appointment_hour']}",
                            "resourceId": "a", 
                        }
                        events.append(event)
                    
                    current_date = datetime.now()
                    year = current_date.year
                    month = current_date.month
                    initial_date = f"{year}-{month:02d}-01"
                    calendar_options = {
                        "initialDate": initial_date,
                        "initialView": "listMonth",  
                    }

                    state = calendar(events=events, options=calendar_options, key="my_calendar")   

                    st.write(state)
                else:
                    st.write("Вие нямате записани часове")
    if role_user == 'admin':
        with st.sidebar:
            selected = st.selectbox('MedAssist', ['Admin panel'], index=0, format_func=lambda x: ' Admin panel' if x == 'Admin panel' else x)
        if selected == 'Admin panel':
            st.header("Нов доктор")
            doctor_first_name = st.text_input("Име")
            doctor_sec_name = st.text_input("Фамилия")
            doc_city = st.text_input("Град")
            doc_tel = st.text_input("тел.номер")
            doctor_specialty = st.text_input("Специалност")
            doctor_email = st.text_input("Имейл")
            if st.button("Add Doctor"):
                doc_username = 'doc_' + doctor_first_name
                doc_pass = doctor_first_name + doctor_sec_name + '123'
                print(doc_username)
                if doctor_first_name and doctor_specialty and doctor_email and doc_city and doctor_sec_name and doc_tel:
                    save_doc_info(doctor_first_name,doctor_sec_name,doctor_email,doctor_specialty,doc_city,doc_tel)
                    register_new_usr(doctor_first_name,doctor_email,doc_username,doc_pass)
                    save_user_profile(conn,doc_username,None,None,None,None,None,None,'doc')
                    set_default_schedule(doc_username)
                    set_default_schedule_av_hours(doc_username)
                else:
                    st.warning("Please fill in all the information.")
    if role_user=='doc':
        with st.sidebar:
        
            selected = option_menu('MedAssist',
                            
                            [
                                'Вашият график',
                                'Записани часове',
                            ],
                            icons=['person','bandaid'],
                            default_index=0)
        if selected == "Вашият график":
            st.header(f"Здравейте {username}")
            
            doctor_schedule = get_doctor_schedule(username)
            if st.session_state.data:
                st.write("Your Schedule:")
                for day_schedule in doctor_schedule:
                    if len(day_schedule) >= 4:
                        day, available_hours, start_time, end_time = day_schedule[:4]
                        if day == 'Monday':
                            print(start_time)
                            print(end_time)
                            st.write(f"{day}: {start_time} - {end_time}")
                for day_schedule in doctor_schedule:
                    if len(day_schedule) >= 4:
                        day, available_hours, start_time, end_time = day_schedule[:4]
                        if day == 'Tuesday':
                            st.write(f"{day}: {start_time} - {end_time}")
                for day_schedule in doctor_schedule:
                    if len(day_schedule) >= 4:
                        day, available_hours, start_time, end_time = day_schedule[:4]
                        if day == 'Wednesday':
                            st.write(f"{day}: {start_time} - {end_time}")
                for day_schedule in doctor_schedule:
                    if len(day_schedule) >= 4:
                        day, available_hours, start_time, end_time = day_schedule[:4]
                        if day == 'Thursday':
                            st.write(f"{day}: {start_time} - {end_time}")
                for day_schedule in doctor_schedule:
                    if len(day_schedule) >= 4:
                        day, available_hours, start_time, end_time = day_schedule[:4]
                        if day == 'Friday':
                            st.write(f"{day}: {start_time} - {end_time}")
                for day_schedule in doctor_schedule:
                    if len(day_schedule) >= 4:
                        day, available_hours, start_time, end_time = day_schedule[:4]
                        if day == 'Saturday':
                            st.write(f"{day}: {start_time} - {end_time}")
                for day_schedule in doctor_schedule:
                    if len(day_schedule) >= 4:
                        day, available_hours, start_time, end_time = day_schedule[:4]
                        if day == 'Sunday':
                            st.write(f"{day}: {start_time} - {end_time}")

                if st.button("Променете графика си:"):
                    st.session_state.data = False
                    st.rerun()
            else:
                st.write("Попълнете вашият график")
                st.write("Работно време за понеделник:")
                col1, col2 = st.columns([1,1])
                not_working_monday = st.checkbox("Not working", key="not_working_monday")
                if not not_working_monday:
                    with col1:
                        start_of_monday = st.time_input("Начало на работния ден")
                    with col2:
                        end_of_monday = st.time_input("Край на работния ден")
                else:
                    start_of_monday, end_of_monday = None, None

                available_hours_to_visit_monday = []
                if start_of_monday and end_of_monday:
                    start_time = datetime.combine(datetime.today(), start_of_monday)
                    end_time = datetime.combine(datetime.today(), end_of_monday)
                    current_time = start_time.time()
                    while current_time <= end_time.time():
                        available_hours_to_visit_monday.append(current_time.strftime('%H:%M'))
                        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=20)).time()
                    start_time = start_time.strftime('%H:%M:%S') if start_time else None
                    end_time = end_time.strftime('%H:%M:%S') if end_time else None
                    save_doctor_schedule(username, 'Monday', available_hours_to_visit_monday, start_time, end_time)
                else:
                    save_doctor_schedule(username, 'Monday', available_hours_to_visit_monday, 'Not', 'working')
                st.write("Работно време за вторник:")
                col1, col2 = st.columns([1,1])
                not_working_tuesday = st.checkbox("Not working", key="not_working_tuesday")
                if not not_working_tuesday:
                    with col1:
                        start_of_tuesday = st.time_input("Начало на работния ден ")
                    with col2:
                        end_of_tuesday = st.time_input("Край на работния ден ")
                else:
                    start_of_tuesday, end_of_tuesday = None, None
                available_hours_to_visit_tuesday = []
                if start_of_tuesday and end_of_tuesday:
                    start_time = datetime.combine(datetime.today(), start_of_tuesday)
                    end_time = datetime.combine(datetime.today(), end_of_tuesday)
                    current_time = start_time.time()
                    while current_time <= end_time.time():
                        available_hours_to_visit_tuesday.append(current_time.strftime('%H:%M'))
                        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=20)).time()
                    start_time = start_time.strftime('%H:%M:%S') if start_time else None
                    end_time = end_time.strftime('%H:%M:%S') if end_time else None
                    save_doctor_schedule(username, 'Tuesday', available_hours_to_visit_tuesday, start_time, end_time)
                else:
                    save_doctor_schedule(username, 'Tuesday', available_hours_to_visit_tuesday, 'Not', 'working')
                st.write("Работно време за сряда:")
                col1, col2 = st.columns([1,1])
                not_working_wednesday = st.checkbox("Not working", key="not_working_wednesday")
                if not not_working_wednesday:
                    with col1:
                        start_of_wednesday = st.time_input("Начало на работния ден  ")
                    with col2:
                        end_of_wednesday = st.time_input("Край на работния ден  ")
                else:
                    start_of_wednesday, end_of_wednesday = None, None
                available_hours_to_visit_wednesday = []
                if start_of_wednesday and end_of_wednesday:
                    start_time = datetime.combine(datetime.today(), start_of_wednesday)
                    end_time = datetime.combine(datetime.today(), end_of_wednesday)
                    current_time = start_time.time()
                    while current_time <= end_time.time():
                        available_hours_to_visit_wednesday.append(current_time.strftime('%H:%M'))
                        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=20)).time()
                    start_time = start_time.strftime('%H:%M:%S') if start_time else None
                    end_time = end_time.strftime('%H:%M:%S') if end_time else None
                    save_doctor_schedule(username, 'Wednesday', available_hours_to_visit_wednesday, start_time, end_time)
                else:
                    save_doctor_schedule(username, 'Wednesday', available_hours_to_visit_wednesday, 'Not', 'working')
                st.write("Работно време за четвъртък:")
                col1, col2 = st.columns([1,1])
                not_working_thursday = st.checkbox("Not working", key="not_working_thursday")
                if not not_working_thursday:
                    with col1:
                        start_of_thursday = st.time_input("Начало на работния ден   ")
                    with col2:
                        end_of_thursday = st.time_input("Край на работния ден   ")
                else:
                    start_of_thursday, end_of_thursday = None, None
                available_hours_to_visit_thursday = []
                if start_of_thursday and end_of_thursday:
                    start_time = datetime.combine(datetime.today(), start_of_thursday)
                    end_time = datetime.combine(datetime.today(), end_of_thursday)
                    current_time = start_time.time()
                    while current_time <= end_time.time():
                        available_hours_to_visit_thursday.append(current_time.strftime('%H:%M'))
                        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=20)).time()
                    start_time = start_time.strftime('%H:%M:%S') if start_time else None
                    end_time = end_time.strftime('%H:%M:%S') if end_time else None
                    save_doctor_schedule(username, 'Thursday', available_hours_to_visit_thursday, start_time, end_time)
                else:
                    save_doctor_schedule(username, 'Thursday', available_hours_to_visit_thursday, 'Not', 'working')
                st.write("Работно време за петък:")
                col1, col2 = st.columns([1,1])
                not_working_friday = st.checkbox("Not working", key="not_working_friday")
                if not not_working_friday:
                    with col1:
                        start_of_friday = st.time_input("Начало на работния ден    ")
                    with col2:
                        end_of_friday = st.time_input("Край на работния ден    ")
                else:
                    start_of_friday, end_of_friday = None, None
                available_hours_to_visit_friday = []
                if start_of_friday and end_of_friday:
                    start_time = datetime.combine(datetime.today(), start_of_friday)
                    end_time = datetime.combine(datetime.today(), end_of_friday)
                    current_time = start_time.time()
                    while current_time <= end_time.time():
                        available_hours_to_visit_friday.append(current_time.strftime('%H:%M'))
                        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=20)).time()
                    start_time = start_time.strftime('%H:%M:%S') if start_time else None
                    end_time = end_time.strftime('%H:%M:%S') if end_time else None
                    save_doctor_schedule(username, 'Friday', available_hours_to_visit_friday, start_time, end_time)
                else:
                    save_doctor_schedule(username, 'Friday', available_hours_to_visit_friday, 'Not', 'working')
                st.write("Работно време за събота:")
                col1, col2 = st.columns([1,1])
                not_working_saturday = st.checkbox("Not working", key="not_working_saturday")
                if not not_working_saturday:
                    with col1:
                        start_of_saturday = st.time_input("Начало на работния ден     ")
                    with col2:
                        end_of_saturday = st.time_input("Край на работния ден     ")
                else:
                    start_of_saturday, end_of_saturday = None, None
                available_hours_to_visit_saturday = []
                if start_of_saturday and end_of_saturday:
                    start_time = datetime.combine(datetime.today(), start_of_saturday)
                    end_time = datetime.combine(datetime.today(), end_of_saturday)
                    current_time = start_time.time()
                    while current_time <= end_time.time():
                        available_hours_to_visit_saturday.append(current_time.strftime('%H:%M'))
                        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=20)).time()
                    start_time = start_time.strftime('%H:%M:%S') if start_time else None
                    end_time = end_time.strftime('%H:%M:%S') if end_time else None
                    save_doctor_schedule(username, 'Saturday', available_hours_to_visit_saturday, start_time, end_time)
                else:
                    save_doctor_schedule(username, 'Saturday', available_hours_to_visit_saturday, 'Not', 'working')
                st.write("Работно време за неделя:")
                col1, col2 = st.columns([1,1])
                not_working_sunday = st.checkbox("Not working", key="not_working_sunday")
                if not not_working_sunday:
                    with col1:
                        start_of_sunday = st.time_input("Начало на работния ден      ")
                    with col2:
                        end_of_sunday = st.time_input("Край на работния ден      ")
                else:
                    start_of_sunday, end_of_sunday = None, None
                available_hours_to_visit_sunday = []
                if start_of_sunday and end_of_sunday:
                    start_time = datetime.combine(datetime.today(), start_of_sunday)
                    end_time = datetime.combine(datetime.today(), end_of_sunday)
                    current_time = start_time.time()
                    while current_time <= end_time.time():
                        available_hours_to_visit_sunday.append(current_time.strftime('%H:%M'))
                        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=20)).time()
                    start_time = start_time.strftime('%H:%M:%S') if start_time else None
                    end_time = end_time.strftime('%H:%M:%S') if end_time else None
                    save_doctor_schedule(username, 'Sunday', available_hours_to_visit_sunday, start_time, end_time)
                else:
                    save_doctor_schedule(username, 'Sunday', available_hours_to_visit_sunday, 'Not', 'working')
                if st.button("Запази"):
                    st.session_state.data = True
                    st.rerun()
        if selected == "Записани часове":
            doctor_appointments = get_doctor_appointments(username)  # Fetch appointments for the doctor
            if doctor_appointments:
                appointments_for_calendar = []  # A separate list to hold appointments for the calendar
                for appointment in doctor_appointments:
                    patient_username, appointment_date, appointment_hour = appointment
                    appointments_for_calendar.append(
                        {
                            "patient_username": patient_username,
                            "appointment_date": appointment_date,
                            "appointment_hour": appointment_hour,
                        }
                    )
                events = []
                for appointment in appointments_for_calendar:
                    event = {
                        "title": appointment["patient_username"],
                        "color": "#FF4B4B",  # Red color
                        "start": f"{appointment['appointment_date']}T{appointment['appointment_hour']}",
                        "end": f"{appointment['appointment_date']}T{appointment['appointment_hour']}",
                        "resourceId": "a",  # resourceId - modify this as needed
                    }
                    events.append(event)
                current_date = datetime.now()
                year = current_date.year
                month = current_date.month
                initial_date = f"{year}-{month:02d}-01"
                calendar_options = {
                    "initialDate": initial_date,
                    "initialView": "listMonth",
                }
                state = calendar(events=events, options=calendar_options, key="my_calendar")   
                st.write(state)
            else:
                st.write("Нямате записани часове за следващия месец")