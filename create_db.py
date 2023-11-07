"""
creates databse for web app.
usage: python scripts/create_db.py

sqlite commands:
sqlite quizHack.db
.schema

"""
import sqlite3

conn = sqlite3.connect("pubQuiz.db")

# cursor object to execute SQL commands
cursor = conn.cursor()

# create the "users" table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        passhash TEXT NOT NULL
    )
"""
)

# create "user_stats"
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS user_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        last_score INTEGER,
        high_score INTEGER,
        user_time INTEGER,  -- Add the user_time field,
        badges TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
"""
)

# commit
conn.commit()
conn.close()

print("Database 'quizHack' created successfully.")
