import sqlite3
import re
import PyPDF2
import streamlit as st


def create_connection():
    conn = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
    return conn

def create_user_profiles_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            age INTEGER,
            sex TEXT,
            pregnancies INTEGER,
            height REAL,
            weight REAL,
            result INTEGER,
            role REAL 
        )
    ''')
    cursor.execute('''
        PRAGMA table_info(user_profiles)
    ''')
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'result' not in column_names:
        cursor.execute('''
            ALTER TABLE user_profiles
            ADD COLUMN result INTEGER
        ''')
        conn.commit()
    if 'role' not in column_names:
        cursor.execute('''
            ALTER TABLE user_profiles
            ADD COLUMN role REAL
        ''')
        conn.commit()


def change_user_role(conn, user_id, new_role):
    try:
        save_user_role(conn, user_id, new_role)
        print(f"Role updated successfully for user '{user_id}' to '{new_role}'")
    except sqlite3.Error as e:
        print(f"Error occurred while updating user role: {e}")

def save_user_profile(conn, user_id, age, sex, pregnancies, height, weight, result, role):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id FROM user_profiles WHERE user_id = ?
        ''', (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.execute('''
                UPDATE user_profiles
                SET age=?, sex=?, pregnancies=?, height=?, weight=?, result=?, role=?
                WHERE user_id=?
            ''', (age, sex, pregnancies, height, weight, result, role, user_id))
        else:
            cursor.execute('''
                INSERT INTO user_profiles (user_id, age, sex, pregnancies, height, weight, result, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, age, sex, pregnancies, height, weight, result, role))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error occurred: {e}")

def init_session_state():
    if 'data' not in st.session_state:
        st.session_state.data = True

def check_parameters_filled(age, sex, height, kilo):
    if age is None or sex is None or height is None or kilo is None or age == 0 or height == 0 or kilo == 0:
        return False  
    return True  

def save_appointment(doctor_username, user_id, appointment_date, appointment_hour):
    try:
        conn = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO appointed_hours (doctor_username, user_id, appointment_date, appointment_hour)
            VALUES (?, ?, ?, ?)
        ''', (doctor_username, user_id, appointment_date, appointment_hour))

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Error saving appointment: {e}")
def save_user_result(conn, user_id, result):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_profiles
            SET result = ?
            WHERE user_id = ?
        ''', (result, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error occurred: {e}")

def save_user_role(conn, user_id, role):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_profiles
            SET role = ?
            WHERE user_id = ?
        ''', (role, user_id))
        conn.commit()
        print(f"Role updated successfully for user '{user_id}' to '{role}'")
    except sqlite3.Error as e:
        print(f"Error occurred: {e}")

def get_user_profile(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    return cursor.fetchone()
def get_age_of_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT age FROM user_profiles WHERE user_id = ?', (user_id,))
    age = cursor.fetchone()
    return age[0] if age else None
def get_height_of_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT height FROM user_profiles WHERE user_id = ?', (user_id,))
    height = cursor.fetchone()
    return height[0] if height else None
def get_result_of_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT result FROM user_profiles WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None
def get_sex_of_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT sex FROM user_profiles WHERE user_id = ?', (user_id,))
    sex = cursor.fetchone()
    return sex[0] if sex else None

def get_kilo_of_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT weight FROM user_profiles WHERE user_id = ?', (user_id,))
    weight = cursor.fetchone()
    return weight[0] if weight else None
def get_pregnancies_of_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT pregnancies FROM user_profiles WHERE user_id = ?', (user_id,))
    pregnancies = cursor.fetchone()
    return pregnancies[0] if pregnancies else None
def get_user_role(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM user_profiles WHERE user_id = ?', (user_id,))
    role = cursor.fetchone()
    return role[0] if role else None

def get_user_appointments(username):
    conn = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
    cursor = conn.cursor()

    # Fetch appointments for the given username
    cursor.execute("SELECT doctor_username, appointment_date, appointment_hour FROM appointed_hours WHERE user_id = ?", (username,))
    appointments = cursor.fetchall()

    conn.close()
    return appointments

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]
        text += page.extract_text()
    return text