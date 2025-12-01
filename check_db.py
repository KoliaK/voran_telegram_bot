# USE THIS SCRIPT TO CHECK USERS IN bot.db
import sqlite3

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

print("--- USERS IN DATABASE ---")
for row in rows:
    print(row)

conn.close()