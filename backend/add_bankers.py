import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

bankers = [
    ("Rajesh Kumar",  "State Bank of India", "SBIN0000001"),
    ("Priya Sharma",  "HDFC Bank",           "HDFC0001234"),
    ("Arun Mehta",    "ICICI Bank",          "ICIC0005678"),
    ("Sunita Reddy",  "Axis Bank",           "UTIB0004321"),
]

for b in bankers:
    c.execute('''
        INSERT INTO bankers (name, bank_name, ifsc, total_customers, approval, rejection, manual)
        VALUES (?, ?, ?, 0, 0, 0, 0)
    ''', b)

conn.commit()
conn.close()
print("Bankers added successfully!")
