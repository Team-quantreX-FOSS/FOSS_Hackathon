import sqlite3
conn = sqlite3.connect('users.db')
c = conn.cursor()

print("BANKERS columns and data:")
c.execute("PRAGMA table_info(bankers)")
cols = c.fetchall()
for col in cols:
    print(f"  index {col[0]}: {col[1]}")

print("\nBANKERS rows:")
c.execute("SELECT * FROM bankers")
for r in c.fetchall():
    print(" ", r)

print("\nUSERS rows:")
c.execute("SELECT id, name, age, phone, loanAmount, allocated_banker, loan_status FROM users")
for r in c.fetchall():
    print(" ", r)

conn.close()