import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

print("Current users with age=0:")
c.execute("SELECT id, name, age FROM users WHERE age=0 OR age IS NULL")
rows = c.fetchall()
for r in rows:
    print(f"  id={r[0]}, name={r[1]}, age={r[2]}")

if not rows:
    print("No users with age=0 found.")
else:
    print("\nUpdating ages manually...")
    # You can change these ages to the correct values
    for r in rows:
        age = input(f"Enter age for {r[1]} (id={r[0]}) or press Enter to skip: ").strip()
        if age and age.isdigit():
            c.execute("UPDATE users SET age=? WHERE id=?", (int(age), r[0]))
            print(f"  Updated {r[1]} age to {age}")

conn.commit()
conn.close()
print("\nDone.")
