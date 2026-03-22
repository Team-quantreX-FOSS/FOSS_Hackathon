import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

print("=" * 50)
print("TABLES IN DB:")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
for t in tables:
    print(" -", t[0])

print("\n" + "=" * 50)
print("BANKERS:")
try:
    c.execute("PRAGMA table_info(bankers)")
    cols = [col[1] for col in c.fetchall()]
    print("Columns:", cols)
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    print(f"Count: {len(rows)}")
    for r in rows:
        print(" ", r)
except Exception as e:
    print("Error:", e)

print("\n" + "=" * 50)
print("USERS (loan applications):")
try:
    c.execute("SELECT COUNT(*) FROM users")
    print(f"Count: {c.fetchone()[0]}")
    c.execute("SELECT id, name, phone, loan_status, allocated_banker FROM users")
    for r in c.fetchall():
        print(" ", r)
except Exception as e:
    print("Error:", e)

print("\n" + "=" * 50)
print("USER ACCOUNTS (registered users):")
try:
    c.execute("SELECT * FROM user_accounts")
    rows = c.fetchall()
    print(f"Count: {len(rows)}")
    for r in rows:
        print(" ", r)
except Exception as e:
    print("Table may not exist:", e)

conn.close()
