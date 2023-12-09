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

def set_default_schedule(username):
    try:
        save_doctor_schedule( username, 'Monday', None, '09:00', '17:00')
        save_doctor_schedule( username, 'Tuesday', None, '08:00', '17:00')
        save_doctor_schedule( username, 'Wednesday', None, '08:00', '19:00')
        save_doctor_schedule( username, 'Thursday', None, '12:00', '17:00')
        save_doctor_schedule( username, 'Friday', None, '08:00', '17:00')
        save_doctor_schedule( username, 'Saturday', None, 'Not', 'working')
        save_doctor_schedule( username, 'Sunday', None, 'Not', 'working')
        available_hours_to_visit = []
        current_time = start_time.time()
        while current_time <= end_time.time():
            available_hours_to_visit.append(current_time.strftime('%H:%M'))
            current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=20)).time()
        start_time = start_time.strftime('%H:%M:%S') if start_time else None
        end_time = end_time.strftime('%H:%M:%S') if end_time else None
        save_doctor_schedule( username, 'Monday', available_hours_to_visit, '09:00', '17:00')
        save_doctor_schedule( username, 'Tuesday', available_hours_to_visit, '08:00', '17:00')
        save_doctor_schedule( username, 'Wednesday', available_hours_to_visit, '08:00', '19:00')
        save_doctor_schedule( username, 'Thursday', available_hours_to_visit, '12:00', '17:00')
        save_doctor_schedule( username, 'Friday', available_hours_to_visit, '08:00', '17:00')
        save_doctor_schedule( username, 'Saturday', available_hours_to_visit, 'Not', 'working')
        save_doctor_schedule( username, 'Sunday', available_hours_to_visit, 'Not', 'working')
    except:
        print("Error setting default schedule")
def set_default_schedule_av_hours(username):
    working_hours = {
        'Monday': ('09:00', '17:00'),
        'Tuesday': ('08:00', '17:00'),
        'Wednesday': ('08:00', '19:00'),
        'Thursday': ('12:00', '17:00'),
        'Friday': ('08:00', '17:00'),
        'Saturday': None,  # Not working
        'Sunday': None     # Not working
    }

    try:
        # Set default available hours for each day
        for day, (start_time, end_time) in working_hours.items():
            if start_time and end_time:  # Check if the day is a working day
                current_time = datetime.strptime(start_time, '%H:%M')
                end = datetime.strptime(end_time, '%H:%M')
                available_hours_to_visit = []

                while current_time <= end:
                    available_hours_to_visit.append(current_time.strftime('%H:%M'))
                    current_time += timedelta(minutes=20)  # Increment by 20 minutes for free slots

                # Save doctor's schedule
                save_doctor_schedule(username, day, available_hours_to_visit, start_time, end_time)
            else:
                # If not working, set as 'Not working'
                save_doctor_schedule(username, day, [], 'Not working', 'Not working')

    except Exception as e:
        print(f"Error setting default schedule: {e}")

def save_doctor_schedule(username, day, available_hours, start_time, end_time):
    try:
        dc_schedule = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
        c = dc_schedule.cursor()

        c.execute("SELECT * FROM doctor_schedule WHERE doctor_username = ? AND day = ?", (username, day))
        existing_schedule = c.fetchone()

        # Serialize the list to a JSON string
        available_hours_json = json.dumps(available_hours)

        

        if existing_schedule:
            # Update existing schedule
            c.execute("UPDATE doctor_schedule SET available_hours = ?, start_time = ?, end_time = ? WHERE doctor_username = ? AND day = ?",
                      (available_hours_json, start_time, end_time, username, day))
        else:
            # Insert a new schedule
            c.execute("INSERT INTO doctor_schedule (doctor_username, day, available_hours, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                      (username, day, available_hours_json, start_time, end_time))

        dc_schedule.commit()
        dc_schedule.close()
    except sqlite3.Error as e:
        print("Error saving doctor schedule:", e)


def get_doctor_schedule(username):
    dc_schedule = sqlite3.connect(r'C:\Users\MSI\Desktop\MedAssist\user_profiles.db')
    c = dc_schedule.cursor()

    c.execute('''
        SELECT day, available_hours, start_time, end_time
        FROM doctor_schedule
        WHERE doctor_username = ?
    ''', (username,))

    schedule = c.fetchall()
    dc_schedule.close()

    # Process the available_hours column to convert JSON string to list
    processed_schedule = []
    for day, available_hours_json, start_time, end_time in schedule:
        available_hours = json.loads(available_hours_json) if available_hours_json else None
        processed_schedule.append((day, available_hours, start_time, end_time))

    return processed_schedule