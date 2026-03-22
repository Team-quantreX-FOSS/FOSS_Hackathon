import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute("SELECT * FROM bankers")
bankers = c.fetchall()

c.execute("PRAGMA table_info(bankers)")
cols = [col[1] for col in c.fetchall()]

for b in bankers:
    row  = dict(zip(cols, b))
    name = row['name']
    bid  = row['id']

    c.execute("SELECT COUNT(*) FROM users WHERE allocated_banker=? AND loan_status='Approved'", (name,))
    approved = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE allocated_banker=? AND loan_status='Rejected'", (name,))
    rejected = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE allocated_banker=? AND loan_status='Manual Review'", (name,))
    manual = c.fetchone()[0]

    total = approved + rejected + manual

    c.execute("UPDATE bankers SET total_customers=?, approval=?, rejection=?, manual=? WHERE id=?",
              (total, approved, rejected, manual, bid))
    print(f"{name}: total={total}, approved={approved}, rejected={rejected}, manual={manual}")

conn.commit()
conn.close()
print("Done - counts fixed.")
