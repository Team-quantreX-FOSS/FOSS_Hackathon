from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__, static_folder='static', template_folder='templates')

# ------------------ INIT DB ------------------
def init_db():
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
        banker_id TEXT UNIQUE,
        total_customers INTEGER DEFAULT 0,
        approval INTEGER DEFAULT 0,
        rejection INTEGER DEFAULT 0,
        manual INTEGER DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        admin_id TEXT UNIQUE
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/user_dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/banker_dashboard')
def banker_dashboard():
    return render_template('banker_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin_borrowers')
def admin_borrowers():
    return render_template('admin_borrowers.html')

@app.route('/admin_bankers')
def admin_bankers():
    return render_template('admin_bankers.html')

@app.route('/loan_check')
def loan_check():
    return render_template('loan_check.html')

@app.route('/financial_advisory')
def financial_advisory():
    return render_template('financial_advisory.html')

@app.route('/user_profile')
def user_profile():
    return render_template('user_profile.html')

@app.route('/banker_profile')
def banker_profile():
    return render_template('banker_profile.html')

@app.route('/admin_profile')
def admin_profile():
    return render_template('admin_profile.html')

@app.route('/banker_review')
def banker_review():
    return render_template('banker_review.html')

# ------------------ REGISTER BANKER ------------------
@app.route('/register_banker', methods=['POST'])
def register_banker():
    data      = request.json
    name      = data.get('name', '').strip()
    banker_id = data.get('banker_id', '').strip()
    bank_name = data.get('bank_name', '').strip()
    branch    = data.get('branch', '').strip()
    ifsc      = data.get('ifsc', '').strip()

    if not name or not banker_id or not bank_name or not ifsc:
        return jsonify({"error": "All fields are required."}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Add branch column if missing
    c.execute("PRAGMA table_info(bankers)")
    cols = [col[1] for col in c.fetchall()]
    if 'banker_id' not in cols:
        c.execute("ALTER TABLE bankers ADD COLUMN banker_id TEXT")
    if 'branch' not in cols:
        c.execute("ALTER TABLE bankers ADD COLUMN branch TEXT")

    c.execute("SELECT id FROM bankers WHERE banker_id=?", (banker_id,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Banker ID already registered."}), 400

    c.execute('''
        INSERT INTO bankers (name, bank_name, branch, ifsc, banker_id, total_customers, approval, rejection, manual)
        VALUES (?, ?, ?, ?, ?, 0, 0, 0, 0)
    ''', (name, bank_name, branch, ifsc, banker_id))

    conn.commit()
    conn.close()
    return jsonify({"message": "Banker registered successfully."})

# ------------------ REGISTER ADMIN ------------------
@app.route('/register_admin', methods=['POST'])
def register_admin():
    data     = request.json
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip()
    admin_id = data.get('admin_id', '').strip()

    if not name or not email or not admin_id:
        return jsonify({"error": "All fields are required."}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM admins WHERE admin_id=?", (admin_id,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Admin ID already exists."}), 400

    c.execute("INSERT INTO admins (name, email, admin_id) VALUES (?, ?, ?)",
              (name, email, admin_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Admin registered successfully."})

# ------------------ APPLY LOAN ------------------
@app.route('/apply_loan', methods=['GET', 'POST'])
def apply_loan():
    if request.method == 'GET':
        return render_template('apply_loan.html')

    data = request.json
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Check if any banker exists
    c.execute("SELECT COUNT(*) FROM bankers")
    banker_count = c.fetchone()[0]

    # Do NOT auto-assign — banker will pick up manually
    c.execute('''
        INSERT INTO users
        (name, age, phone, loanAmount, loanType, tenure, emi, risk_score, allocated_banker, loan_status, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'), data.get('age', 0), data.get('phone'),
        data.get('loanAmount'), data.get('loanType'), data.get('tenure'),
        data.get('emi'), data.get('risk_score'),
        None,  # no auto-assign
        "Pending", ""
    ))
    conn.commit()
    conn.close()

    if banker_count == 0:
        return jsonify({"message": "no_banker"})
    return jsonify({"message": "submitted"})

# ------------------ BANKER PICKS UP A LOAN ------------------
@app.route('/pickup_loan', methods=['POST'])
def pickup_loan():
    data      = request.json
    user_id   = data.get('user_id')
    banker_name = data.get('banker_name', '').strip()

    if not user_id or not banker_name:
        return jsonify({"error": "Missing data."}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Only pick up if not already assigned
    c.execute("SELECT allocated_banker FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Application not found."}), 404
    if row[0]:
        conn.close()
        return jsonify({"error": "Already picked up by another banker."}), 400

    c.execute("UPDATE users SET allocated_banker=?, loan_status=? WHERE id=?",
              (banker_name, "Picked Up", user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Picked up successfully."})

# ------------------ SAVE USER ------------------
@app.route('/save', methods=['POST'])
def save_data():
    data = request.json
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name, phone, loan_status, reason) VALUES (?, ?, ?, ?)",
              (data.get('name'), data.get('phone'), "Pending", ""))
    conn.commit()
    conn.close()
    return jsonify({"message": "Saved"})

# ------------------ GET USERS ------------------
@app.route('/api/users')
def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    users = []
    for r in rows:
        users.append({
            "id": r[0], "name": r[1], "age": r[2], "phone": r[3],
            "loanAmount": r[4], "loanType": r[5], "tenure": r[6],
            "emi": r[7], "score": r[8], "banker": r[9],
            "status": r[10], "reason": r[11]
        })
    return jsonify(users)

# ------------------ GET BANKERS ------------------
@app.route('/api/bankers')
def get_bankers():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bankers)")
    col_info = c.fetchall()
    cols = [col[1] for col in col_info]
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    conn.close()
    bankers = []
    for b in rows:
        row = dict(zip(cols, b))
        bankers.append({
            "id":             row.get("id", ""),
            "name":           row.get("name", ""),
            "bankName":       row.get("bank_name", ""),
            "branch":         row.get("branch", ""),
            "ifsc":           row.get("ifsc", ""),
            "bankerId":       row.get("banker_id", row.get("ifsc","")),
            "totalCustomers": row.get("total_customers", 0),
            "approval":       row.get("approval", 0),
            "rejection":      row.get("rejection", 0),
            "manual":         row.get("manual", 0)
        })
    return jsonify(bankers)

# ------------------ GET BANKS (only registered) ------------------
@app.route('/api/banks')
def get_banks():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bankers)")
    cols = [col[1] for col in c.fetchall()]
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    conn.close()
    seen = set()
    banks = []
    for r in rows:
        row = dict(zip(cols, r))
        key = row.get("bank_name","")
        if key not in seen:
            seen.add(key)
            banks.append({"name": key, "branch": row.get("branch",""), "ifsc": row.get("ifsc","")})
    return jsonify(banks)

# ------------------ BANKER ACTION ------------------
@app.route('/banker_action', methods=['POST'])
def banker_action():
    data    = request.json
    user_id = data.get('user_id')
    action  = data.get('action')
    reason  = data.get('reason', '')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Get CURRENT status before updating
    c.execute("SELECT loan_status, allocated_banker FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    current_status = row[0]
    banker         = row[1]

    # Update the loan status
    c.execute("UPDATE users SET loan_status=?, reason=? WHERE id=?", (action, reason, user_id))

    if banker:
        # Only count as new customer if this is the FIRST final action
        # i.e. previous status was Pending or Picked Up (not already Approved/Rejected/Manual)
        first_action = current_status in ("Pending", "Picked Up")

        # Reset previous counter if status is changing FROM a final state
        # e.g. was Approved, now setting to Rejected — undo approval, add rejection
        if current_status == "Approved" and action != "Approved":
            c.execute("UPDATE bankers SET approval=MAX(0,approval-1) WHERE name=?", (banker,))
        elif current_status == "Rejected" and action != "Rejected":
            c.execute("UPDATE bankers SET rejection=MAX(0,rejection-1) WHERE name=?", (banker,))
        elif current_status == "Manual Review" and action != "Manual Review":
            c.execute("UPDATE bankers SET manual=MAX(0,manual-1) WHERE name=?", (banker,))

        # Add new action counter
        if action == "Approved":
            c.execute("UPDATE bankers SET approval=approval+1 WHERE name=?", (banker,))
        elif action == "Rejected":
            c.execute("UPDATE bankers SET rejection=rejection+1 WHERE name=?", (banker,))
        elif action == "Manual Review":
            c.execute("UPDATE bankers SET manual=manual+1 WHERE name=?", (banker,))

        # Only increment total_customers once (first time a final action is taken)
        if first_action:
            c.execute("UPDATE bankers SET total_customers=total_customers+1 WHERE name=?", (banker,))

    conn.commit()
    conn.close()
    return jsonify({"message": "Action recorded"})

# ------------------ DELETE USER ------------------
@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

# ------------------ RESET SYSTEM ------------------
@app.route('/reset_all', methods=['POST'])
def reset_all():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users")
    c.execute("DELETE FROM bankers")
    conn.commit()
    conn.close()
    return jsonify({"message": "Reset successful"})

# ------------------ UPDATE STATUS ------------------
@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET loan_status=?, reason=? WHERE id=?",
              (data['status'], data['reason'], data['id']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

# ------------------ USER NOTIFICATION ------------------
@app.route('/get_status/<phone>')
def get_status(phone):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Also accept optional name param to identify correct user
    name = request.args.get('name', '').strip()
    if name:
        c.execute('''SELECT loan_status, reason, allocated_banker
                     FROM users WHERE phone=? AND name=? ORDER BY id DESC LIMIT 1''', (phone, name))
    else:
        c.execute('''SELECT loan_status, reason, allocated_banker
                     FROM users WHERE phone=? ORDER BY id DESC LIMIT 1''', (phone,))
    data = c.fetchone()
    conn.close()
    if data:
        return jsonify({"status": data[0], "reason": data[1], "banker": data[2] or ""})
    return jsonify({"status": "No Application", "reason": "", "banker": ""})

# ------------------ BANKER DASHBOARD API ------------------
@app.route('/users')
def api_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    users = []
    for r in rows:
        users.append([
            r[0], r[1], r[3],
            r[4] if r[4] else 0, r[5] if r[5] else "",
            r[6] if r[6] else 0, r[7] if r[7] else 0,
            r[8] if r[8] else 0, r[9] if r[9] else "",
            r[10] if r[10] else "Pending", r[11] if r[11] else ""
        ])
    return jsonify(users)

# ------------------ GET BORROWERS FOR ADMIN ------------------
@app.route('/api/borrowers')
def api_borrowers():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    borrowers = []
    for r in rows:
        borrowers.append({
            "id": r[0], "name": r[1], "age": r[2], "phone": r[3],
            "loanAmount": r[4], "loanType": r[5], "tenure": r[6],
            "emi": r[7], "risk_score": r[8], "allocated_banker": r[9],
            "loan_status": r[10], "reason": r[11]
        })
    return jsonify(borrowers)

# ------------------ GET BANKERS FOR ADMIN ------------------
@app.route('/api/admin_bankers')
def api_admin_bankers():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bankers)")
    col_info = c.fetchall()
    cols = [col[1] for col in col_info]
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    conn.close()
    bankers = []
    for b in rows:
        row = dict(zip(cols, b))
        bankers.append({
            "id":             row.get("id", ""),
            "name":           row.get("name", ""),
            "bank_name":      row.get("bank_name", ""),
            "branch":         row.get("branch", ""),
            "ifsc":           row.get("ifsc", ""),
            "banker_id":      row.get("banker_id", row.get("ifsc","")),
            "total_customers":row.get("total_customers", 0),
            "approval":       row.get("approval", 0),
            "rejection":      row.get("rejection", 0),
            "manual":         row.get("manual", 0)
        })
    return jsonify(bankers)


# ------------------ LOAN REQUESTS PAGE ------------------
@app.route('/loan_requests')
def loan_requests():
    return render_template('loan_requests.html')


# ------------------ LOAN REQUESTS PAGE ------------------
@app.route('/register_user', methods=['POST'])
def register_user():
    data     = request.json
    name     = data.get('name', '').strip()
    phone    = data.get('phone', '').strip()
    username = data.get('username', '').strip()

    if not name or not username:
        return jsonify({"error": "Name and username are required."}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Check duplicate username in a separate registrations table
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        username TEXT UNIQUE
    )
    ''')

    c.execute("SELECT id FROM user_accounts WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Username already taken."}), 400

    c.execute("INSERT INTO user_accounts (name, phone, username) VALUES (?,?,?)",
              (name, phone, username))
    conn.commit()
    conn.close()
    return jsonify({"message": "User registered successfully."})


# ------------------ CHECK USERNAME ------------------
@app.route('/check_username', methods=['POST'])
def check_username():
    data     = request.json
    username = data.get('username','').strip()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, username TEXT UNIQUE
    )''')
    c.execute("SELECT id FROM user_accounts WHERE username=?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return jsonify({"exists": exists})


# ------------------ GET USER ACCOUNTS FOR ADMIN ------------------
@app.route('/api/user_accounts')
def get_user_accounts():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, username TEXT UNIQUE
    )''')
    c.execute("SELECT * FROM user_accounts")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"phone":r[2],"username":r[3]} for r in rows])


# ------------------ GET BANKER BY ID ------------------
@app.route('/api/get_banker/<banker_id>')
def get_banker_by_id(banker_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bankers)")
    cols = [col[1] for col in c.fetchall()]
    c.execute("SELECT * FROM bankers WHERE banker_id=?", (banker_id,))
    row = c.fetchone()
    conn.close()
    if row:
        r = dict(zip(cols, row))
        return jsonify({"name": r.get("name",""), "bankName": r.get("bank_name",""), "ifsc": r.get("ifsc",""), "branch": r.get("branch","")})
    return jsonify({"error": "Not found"}), 404

# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
