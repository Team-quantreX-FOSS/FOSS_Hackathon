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
    ifsc      = data.get('ifsc', '').strip()

    if not name or not banker_id or not bank_name or not ifsc:
        return jsonify({"error": "All fields are required."}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM bankers WHERE banker_id=?", (banker_id,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Banker ID already registered."}), 400

    c.execute('''
        INSERT INTO bankers (name, bank_name, ifsc, banker_id, total_customers, approval, rejection, manual)
        VALUES (?, ?, ?, ?, 0, 0, 0, 0)
    ''', (name, bank_name, ifsc, banker_id))

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
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    conn.close()
    bankers = []
    for b in rows:
        bankers.append({
            "id": b[0], "name": b[1], "bankName": b[2],
            "ifsc": b[3], "bankerId": b[4], "totalCustomers": b[5],
            "approval": b[6], "rejection": b[7], "manual": b[8]
        })
    return jsonify(bankers)

# ------------------ GET BANKS (only registered) ------------------
@app.route('/api/banks')
def get_banks():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT bank_name, ifsc FROM bankers")
    rows = c.fetchall()
    conn.close()
    banks = []
    for r in rows:
        banks.append({"name": r[0], "ifsc": r[1]})
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
    c.execute("UPDATE users SET loan_status=?, reason=? WHERE id=?", (action, reason, user_id))

    c.execute("SELECT allocated_banker FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if row and row[0]:
        banker = row[0]
        if action == "Approved":
            c.execute("UPDATE bankers SET approval=approval+1, total_customers=total_customers+1 WHERE name=?", (banker,))
        elif action == "Rejected":
            c.execute("UPDATE bankers SET rejection=rejection+1, total_customers=total_customers+1 WHERE name=?", (banker,))
        elif action == "Manual Review":
            c.execute("UPDATE bankers SET manual=manual+1, total_customers=total_customers+1 WHERE name=?", (banker,))

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
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    conn.close()
    bankers = []
    for b in rows:
        bankers.append({
            "id": b[0], "name": b[1], "bank_name": b[2],
            "ifsc": b[3], "banker_id": b[4], "total_customers": b[5],
            "approval": b[6], "rejection": b[7], "manual": b[8]
        })
    return jsonify(bankers)


# ------------------ LOAN REQUESTS PAGE ------------------
@app.route('/loan_requests')
def loan_requests():
    return render_template('loan_requests.html')


# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True, port=5050)
