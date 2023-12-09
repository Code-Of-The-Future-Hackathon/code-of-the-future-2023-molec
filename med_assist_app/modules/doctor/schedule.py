import sqlite3

def create_doctor_schedule_table():
    try:
        dc_schedule = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        cursor = dc_schedule.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_username TEXT NOT NULL,
                day TEXT,
                available_hours TEXT,  -- Store the list as a JSON string
                start_time TEXT,
                end_time TEXT,
                UNIQUE(doctor_username, day)
            )
        ''')

        dc_schedule.commit()
        dc_schedule.close()
        print("Doctor schedule created successfully.")
    except sqlite3.Error as e:
        print("Error creating table:", e)