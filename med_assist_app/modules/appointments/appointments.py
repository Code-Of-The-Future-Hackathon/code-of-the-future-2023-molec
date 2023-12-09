import sqlite3

def create_appointed_hours_table():
    try:
        conn = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointed_hours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_username TEXT,
                user_id TEXT,
                appointment_date TEXT,
                appointment_hour TEXT
            )
        ''')

        conn.commit()
        conn.close()
        print("Appointed hours table created successfully.")
    except sqlite3.Error as e:
        print("Error creating appointed hours table:", e)

# Create the appointed_hours table if it doesn't exist
create_appointed_hours_table()