from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__, static_folder='static', template_folder='templates')

# ------------------ INIT DB ------------------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # USERS TABLE
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

    # BANKERS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS bankers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        bank_name TEXT,
        ifsc TEXT,
        total_customers INTEGER DEFAULT 0,
        approval INTEGER DEFAULT 0,
        rejection INTEGER DEFAULT 0,
        manual INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ------------------ STATIC BANK DATA ------------------
banks = [
    {"name": "State Bank of India", "branch": "Mumbai Main", "ifsc": "SBIN0000001"},
    {"name": "HDFC Bank", "branch": "Hyderabad", "ifsc": "HDFC0001234"},
    {"name": "ICICI Bank", "branch": "Delhi", "ifsc": "ICIC0005678"},
    {"name": "Axis Bank", "branch": "Chennai", "ifsc": "UTIB0004321"}
]

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

# ------------------ APPLY LOAN ------------------
@app.route('/apply_loan', methods=['GET', 'POST'])
def apply_loan():
    if request.method == 'GET':
        return render_template('apply_loan.html')
    
    data = request.json
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute("SELECT name FROM bankers ORDER BY RANDOM() LIMIT 1")
    banker = c.fetchone()
    allocated_banker = banker[0] if banker else None

    c.execute('''
        INSERT INTO users
        (name, age, phone, loanAmount, loanType, tenure, emi, risk_score, allocated_banker, loan_status, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('age'),
        data.get('phone'),
        data.get('loanAmount'),
        data.get('loanType'),
        data.get('tenure'),
        data.get('emi'),
        data.get('risk_score'),
        allocated_banker,
        "Pending",
        ""
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Loan application submitted", "allocated_banker": allocated_banker})


# ------------------ SAVE USER ------------------
@app.route('/save', methods=['POST'])
def save_data():
    data = request.json

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''
    INSERT INTO users (name, phone, income, expense, risk_score, loan_status, reason)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['phone'],
        data['income'],
        data['expense'],
        data['risk_score'],
        "Pending",
        ""
    ))

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
            "id": r[0],
            "name": r[1],
            "age": r[2],
            "phone": r[3],
            "loanAmount": r[4],
            "loanType": r[5],
            "tenure": r[6],
            "emi": r[7],
            "score": r[8],
            "banker": r[9],
            "status": r[10],
            "reason": r[11]
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
            "id": b[0],
            "name": b[1],
            "bankName": b[2],
            "ifsc": b[3],
            "totalCustomers": b[4],
            "approval": b[5],
            "rejection": b[6],
            "manual": b[7]
        })
    return jsonify(bankers)

# ------------------ BANKER ACTION ------------------
@app.route('/banker_action', methods=['POST'])
def banker_action():
    data = request.json
    user_id = data.get('user_id')
    action = data.get('action')  # Approved / Rejected / Manual
    reason = data.get('reason', "")

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET loan_status=?, reason=? WHERE id=?", (action, reason, user_id))

    # Update banker stats
    c.execute("SELECT allocated_banker FROM users WHERE id=?", (user_id,))
    banker = c.fetchone()[0]
    if banker:
        if action == "Approved":
            c.execute("UPDATE bankers SET approval = approval + 1, total_customers = total_customers + 1 WHERE name=?", (banker,))
        elif action == "Rejected":
            c.execute("UPDATE bankers SET rejection = rejection + 1, total_customers = total_customers + 1 WHERE name=?", (banker,))
        elif action == "Manual Review":
            c.execute("UPDATE bankers SET manual = manual + 1, total_customers = total_customers + 1 WHERE name=?", (banker,))
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

# ------------------ GET BANKS ------------------
@app.route('/api/banks')
def get_banks():
    return jsonify(banks)

# ------------------ RESET SYSTEM ------------------
@app.route('/reset_all', methods=['POST'])
def reset_all():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users")
    c.execute("DELETE FROM bankers")
    conn.commit()
    conn.close()
    return jsonify({"message": "Reset successful"})  # ✅ FIXED: was missing return

# ------------------ UPDATE STATUS ------------------
@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''
    UPDATE users
    SET loan_status=?, reason=?
    WHERE id=?
    ''', (
        data['status'],
        data['reason'],
        data['id']
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated"})

# ------------------ USER NOTIFICATION ------------------
@app.route('/get_status/<phone>')
def get_status(phone):

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''
    SELECT loan_status, reason FROM users
    WHERE phone=?
    ORDER BY id DESC LIMIT 1
    ''', (phone,))

    data = c.fetchone()
    conn.close()

    if data:
        return jsonify({
            "status": data[0],
            "reason": data[1]
        })
    else:
        return jsonify({
            "status": "No Application",
            "reason": ""
        })

# ------------------ API FOR BANKER DASHBOARD ------------------
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
            r[0],
            r[1],
            r[3],
            r[4] if r[4] else 0,
            r[5] if r[5] else "",
            r[6] if r[6] else 0,
            r[7] if r[7] else 0,
            r[8] if r[8] else 0,
            r[9] if r[9] else "",
            r[10] if r[10] else "Pending",
            r[11] if r[11] else ""
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
            "id": r[0],
            "name": r[1],
            "age": r[2],
            "phone": r[3],
            "loanAmount": r[4],
            "loanType": r[5],
            "tenure": r[6],
            "emi": r[7],
            "risk_score": r[8],
            "allocated_banker": r[9],
            "loan_status": r[10],
            "reason": r[11]
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
            "id": b[0],
            "name": b[1],
            "bank_name": b[2],
            "ifsc": b[3],
            "total_customers": b[4],
            "approval": b[5],
            "rejection": b[6],
            "manual": b[7]
        })
    return jsonify(bankers)

# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True, port=5050)
