import sqlite3
import os

# Delete old DB
if os.path.exists("users.db"):
    os.remove("users.db")
    print("Old users.db deleted.")

# Recreate fresh
conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    phone TEXT,
    loanAmount REAL,
    loanType TEXT,
    tenure INTEGER,
    emi REAL,
    risk_score INTEGER,
    allocated_banker TEXT,
    loan_status TEXT,
    reason TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS bankers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    bank_name TEXT,
    ifsc TEXT,
    total_customers INTEGER DEFAULT 0,
    approval INTEGER DEFAULT 0,
    rejection INTEGER DEFAULT 0,
    manual INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()
print("Fresh users.db created successfully.")
