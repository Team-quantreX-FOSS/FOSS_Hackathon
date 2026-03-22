import sqlite3
from datetime import datetime

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Add missing columns safely
def add_col(table, col, coltype):
    c.execute(f"PRAGMA table_info({table})")
    if col not in [r[1] for r in c.fetchall()]:
        c.execute(f"ALTER TABLE {col} ADD COLUMN {col} {coltype}")
        print(f"Added {col} to {table}")

# Users table - add created_at if missing
c.execute("PRAGMA table_info(users)")
ucols = [r[1] for r in c.fetchall()]
if 'created_at' not in ucols:
    c.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
    print("Added created_at to users")

# Bankers table - add branch if missing
c.execute("PRAGMA table_info(bankers)")
bcols = [r[1] for r in c.fetchall()]
if 'branch' not in bcols:
    c.execute("ALTER TABLE bankers ADD COLUMN branch TEXT DEFAULT ''")
    print("Added branch to bankers")
if 'banker_id' not in bcols:
    c.execute("ALTER TABLE bankers ADD COLUMN banker_id TEXT")
    print("Added banker_id to bankers")

# Create user_accounts if missing
c.execute('''CREATE TABLE IF NOT EXISTS user_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, phone TEXT, username TEXT UNIQUE
)''')

# Create admins if missing
c.execute('''CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, email TEXT, admin_id TEXT UNIQUE
)''')

# Recalculate banker counts from actual user data
c.execute("SELECT * FROM bankers")
bankers = c.fetchall()
c.execute("PRAGMA table_info(bankers)")
cols = [r[1] for r in c.fetchall()]

for b in bankers:
    row  = dict(zip(cols, b))
    name = row['name']
    bid  = row['id']
    c.execute("SELECT COUNT(*) FROM users WHERE allocated_banker=? AND loan_status='Approved'",      (name,))
    approved = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE allocated_banker=? AND loan_status='Rejected'",      (name,))
    rejected = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE allocated_banker=? AND loan_status='Manual Review'", (name,))
    manual   = c.fetchone()[0]
    total    = approved + rejected + manual
    c.execute("UPDATE bankers SET total_customers=?,approval=?,rejection=?,manual=? WHERE id=?",
              (total, approved, rejected, manual, bid))
    print(f"Fixed counts for {name}: total={total}, approved={approved}, rejected={rejected}, manual={manual}")

conn.commit()
conn.close()
print("\nMigration complete. All data preserved.")