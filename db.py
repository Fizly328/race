import sqlite3

def create_tables():
    try:
        with sqlite3.connect('example.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS races_reg(
                id INTEGER PRIMARY KEY,
                name TEXT,
                last_name TEXT,
                car TEXT,
                server TEXT
                )''')
            conn.commit()

    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")



def create_states():
    try:
        with sqlite3.connect('example.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS user_states(
                user_id INTEGER PRIMARY KEY,
                role TEXT NOT NULL,
                state TEXT NOT NULL
                )''')
            conn.commit()

    except:
        print(00)