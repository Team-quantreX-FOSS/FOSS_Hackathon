import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

print("ALL USERS:")
c.execute("SELECT id, name, phone, loan_status, allocated_banker, reason FROM users")
for r in c.fetchall():
    print(f"  id={r[0]}, name={r[1]}, phone={r[2]}, status={r[3]}, banker={r[4]}, reason={r[5]}")

print("\nTesting get_status for each phone:")
c.execute("SELECT DISTINCT phone FROM users")
phones = c.fetchall()
for p in phones:
    phone = p[0]
    c.execute("SELECT loan_status, reason, allocated_banker FROM users WHERE phone=? ORDER BY id DESC LIMIT 1", (phone,))
    row = c.fetchone()
    print(f"  phone={phone} → status={row[0]}, banker={row[2]}")

conn.close()