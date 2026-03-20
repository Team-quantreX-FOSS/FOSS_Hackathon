from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# ------------------ DB INIT ------------------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        income INTEGER,
        expense INTEGER,
        risk_score INTEGER,
        loan_status TEXT,
        reason TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ------------------ HOME ------------------
@app.route('/')
def home():
    return render_template('index.html')

   
@app.route('/index')
def index():
    return render_template('index.html')


# ------------------ USER DASHBOARD ------------------
@app.route('/user_dashboard')
def user_dashboard():
    print("DASHBOARD ROUTE HIT")
    return render_template('user_dashboard.html')


# ------------------ BANKER DASHBOARD ------------------
@app.route('/banker_dashboard')
def banker_dashboard():
    return render_template('banker_dashboard.html')


# ------------------ ADMIN DASHBOARD ------------------
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# ------------------ LOAN CHECK ------------------
@app.route('/loan_check')
def loan_check():
    return render_template('loan_check.html')


# ------------------ FINANCIAL ADVISORY ------------------
@app.route('/financial_advisory')
def financial_advisory():
    return render_template('financial_advisory.html')

# ------------------ APPLY LOAN ------------------
@app.route('/apply_loan')
def apply_loan():
    return render_template('apply_loan.html')


@app.route('/check')
def check():
    return "HELLO WORKING"

# ------------------ SAVE USER FINANCE ------------------
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


# ------------------ GET USERS (BANKER) ------------------
@app.route('/users')
def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    users = c.fetchall()

    conn.close()

    return jsonify(users)


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


if __name__ == '__main__':
    app.run(debug=True)

