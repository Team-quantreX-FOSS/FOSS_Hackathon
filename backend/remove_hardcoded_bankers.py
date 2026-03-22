import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Remove only the hardcoded bankers added by add_bankers.py
# These are identified by their known names
hardcoded = ['Rajesh Kumar', 'Priya Sharma', 'Arun Mehta', 'Sunita Reddy']

for name in hardcoded:
    c.execute("DELETE FROM bankers WHERE name=?", (name,))
    print(f"Removed: {name}")

conn.commit()
conn.close()
print("\nDone. Only hardcoded bankers removed. All other data preserved.")
