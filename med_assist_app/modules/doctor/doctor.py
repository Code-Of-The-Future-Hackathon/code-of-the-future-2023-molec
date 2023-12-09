import sqlite3
import datetime
import json
import streamlit as st

def create_doctor_table():
    try:
        dc_conn = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        cursor = dc_conn.cursor()

        # SQL query to create the table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            specialty TEXT,
            city TEXT,
            telephone TEXT
        );
        '''

        cursor.execute(create_table_query)
        dc_conn.commit()
        dc_conn.close()
        print("Doctor table created successfully.")
    except sqlite3.Error as e:
        print("Error creating table:", e)

def get_day_of_week(date):
    return datetime.strptime(date, '%Y-%m-%d').strftime('%A')

def save_doc_info(first_name, last_name, email, specialty, city, telephone):
    try:
        dc_conn = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        cursor = dc_conn.cursor()

        # SQL query to insert data into the table
        insert_query = '''
        INSERT INTO doctors (first_name, last_name, email, specialty, city, telephone)
        VALUES (?, ?, ?, ?, ?, ?);
        '''

        # Data to be inserted into the table
        data = (first_name, last_name, email, specialty, city, telephone)
        
        cursor.execute(insert_query, data)
        dc_conn.commit()
        dc_conn.close()
        print("Doctor information saved successfully.")
    except sqlite3.Error as e:
        print("Error saving doctor information:", e)

def get_available_hours(doctor_username, day):
    try:
        dc_schedule = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        c = dc_schedule.cursor()

        c.execute("SELECT available_hours FROM doctor_schedule WHERE doctor_username = ? AND day = ?", (doctor_username, day))
        available_hours = c.fetchone()

        dc_schedule.close()

        if available_hours:
            return json.loads(available_hours[0])

    except sqlite3.Error as e:
        print("Error getting available hours:", e)

    return []

def get_doctors_by_specialty_and_city(specialty, city):
    doctors_list = []
    try:
        doc_profiles = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        c = doc_profiles.cursor()

        c.execute("SELECT first_name, last_name FROM doctors WHERE specialty = ? AND city = ?", (specialty, city))
        doctors = c.fetchall()

        doc_profiles.close()

        doctors_list = doctors if doctors else []
    except sqlite3.Error as e:
        print("Error getting doctors by specialty and city:", e)
    return doctors_list

def get_doctor_profile(username):
    try:
        doc_profiles = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        c = doc_profiles.cursor()

        c.execute("SELECT first_name, specialty, city FROM doctors WHERE first_name = ?", (username,))
        profile = c.fetchone()

        doc_profiles.close()

        return profile

    except sqlite3.Error as e:
        print("Error getting doctor profile:", e)

    return None

def get_available_hours_excluding_booked(doctor_username, day):
    try:
        dc_schedule = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        c = dc_schedule.cursor()

        c.execute("SELECT available_hours FROM doctor_schedule WHERE doctor_username = ? AND day = ?", (doctor_username, day))
        available_hours = c.fetchone()

        if available_hours:
            available_hours_list = json.loads(available_hours[0])
            if st.session_state.selected_hour in available_hours_list:
                available_hours_list.remove(st.session_state.selected_hour)

                # Update the doctor_schedule table with the modified available hours
                c.execute("UPDATE doctor_schedule SET available_hours = ? WHERE doctor_username = ? AND day = ?",
                          (json.dumps(available_hours_list), doctor_username, day))
                dc_schedule.commit()

            return available_hours_list

    except sqlite3.Error as e:
        print("Error getting/setting available hours:", e)

    return []

def get_doctor_appointments(doctor_username):
    try:
        conn = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        cursor = conn.cursor()

        # Query appointments for the specified doctor
        cursor.execute('''
            SELECT user_id, appointment_date, appointment_hour 
            FROM appointed_hours 
            WHERE doctor_username = ?
        ''', (doctor_username,))

        doctor_appointments = cursor.fetchall()
        
        conn.close()
        
        return doctor_appointments

    except sqlite3.Error as e:
        print("Error fetching doctor appointments:", e)
        return []
    
