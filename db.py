import sqlite3 # use aiosqlite for high-scale apps

def init_db():
    with sqlite3.connect('bot.db') as conn:
        cursor = conn.cursor()
        # No need for id (...) AUTOINCREMENT since telegram-bot already handles that
        cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            '''
        )
        conn.commit()

def add_user(user_id, username):
    # no need to call init_db() here. We call it once in main.py
    with sqlite3.connect('bot.db') as conn:
        cursor = conn.cursor()
        # ? means "ignore this for now I'll let you know the variables later", since id is an integer
        # INSERT OR IGNORE to handle duplicates safely
        cursor.execute(
            '''
                INSERT OR IGNORE INTO users (id, username) 
                VALUES (? , ?)
            ''', (user_id, username)
        )