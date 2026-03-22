import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

print("Current bankers columns:")
c.execute("PRAGMA table_info(bankers)")
cols = [col[1] for col in c.fetchall()]
print(cols)

# Add banker_id if missing
if 'banker_id' not in cols:
    c.execute("ALTER TABLE bankers ADD COLUMN banker_id TEXT")
    print("Added: banker_id")

# Add branch if missing
if 'branch' not in cols:
    c.execute("ALTER TABLE bankers ADD COLUMN branch TEXT DEFAULT ''")
    print("Added: branch")

# Add user_accounts table if missing
c.execute('''CREATE TABLE IF NOT EXISTS user_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, phone TEXT, username TEXT UNIQUE
)''')

conn.commit()

print("\nFinal bankers columns:")
c.execute("PRAGMA table_info(bankers)")
print([col[1] for col in c.fetchall()])

print("\nAll existing data preserved.")
conn.close()
