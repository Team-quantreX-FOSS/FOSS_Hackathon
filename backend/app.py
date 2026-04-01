from flask import Flask, render_template, request, jsonify, session
import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ── HARDCODED ADMIN CREDENTIALS ───────────────────────────────────────────────
ADMIN_ID       = "ADMViki@2008"
ADMIN_PASSWORD = "Viki@2008"
ADMIN_NAME     = "Moksha"
ADMIN_EMAIL    = "t.moksha.2102@gmail.com"

# ── FILE UPLOAD CONFIG ─────────────────────────────────────────────────────────
UPLOAD_FOLDER   = os.path.join('static', 'uploads')
ALLOWED_EXT     = {'png', 'jpg', 'jpeg', 'pdf', 'webp'}
MAX_CONTENT_LEN = 5 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

app = Flask(__name__, static_folder='static', template_folder='templates')

app.secret_key = "my_super_secret_key_123"
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LEN

# ── SESSION CONFIG ─────────────────────────────────────────────────────────────
app.config['SESSION_COOKIE_SAMESITE']    = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY']    = True
app.config['SESSION_COOKIE_SECURE']      = False  # FIX: Must be False — PythonAnywhere proxies HTTPS, Flask sees HTTP
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3650)
app.config['SESSION_COOKIE_PATH']        = '/'
app.config['SESSION_COOKIE_NAME']        = 'finrisk_session'

import re

def normalize_phone(phone):
    if not phone:
        return ''
    p = re.sub(r'[\s\-]', '', str(phone).strip())
    if p.startswith('+91'):
        p = p[3:]
    elif p.startswith('91') and len(p) == 12:
        p = p[2:]
    elif p.startswith('0') and len(p) == 11:
        p = p[1:]
    return p

def validate_phone(phone):
    p = normalize_phone(phone)
    return bool(re.fullmatch(r'[6-9]\d{9}', p))

def validate_loan_amount(amount):
    try:
        v = float(amount)
        return 1_000 <= v <= 10_000_000
    except (TypeError, ValueError):
        return False

def validate_tenure(tenure):
    try:
        v = int(tenure)
        return 1 <= v <= 360
    except (TypeError, ValueError):
        return False

def validate_risk_score(score):
    try:
        v = int(score)
        return 0 <= v <= 100
    except (TypeError, ValueError):
        return False

def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, age INTEGER, phone TEXT,
        loanAmount REAL, loanType TEXT, tenure INTEGER, emi REAL,
        risk_score INTEGER, allocated_banker TEXT,
        loan_status TEXT, reason TEXT,
        address TEXT, employment TEXT, purpose TEXT,
        aadhar TEXT, pan TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )''')
    c.execute("PRAGMA table_info(users)")
    ucols = [r[1] for r in c.fetchall()]
    for col, typ in [("address","TEXT"),("employment","TEXT"),("purpose","TEXT"),
                     ("aadhar","TEXT"),("pan","TEXT"),("created_at","TEXT")]:
        if col not in ucols:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")

    c.execute('''CREATE TABLE IF NOT EXISTS bankers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, bank_name TEXT, branch TEXT, ifsc TEXT,
        banker_id TEXT UNIQUE, password TEXT,
        total_customers INTEGER DEFAULT 0,
        approval INTEGER DEFAULT 0,
        rejection INTEGER DEFAULT 0,
        manual INTEGER DEFAULT 0
    )''')
    c.execute("PRAGMA table_info(bankers)")
    bcols = [r[1] for r in c.fetchall()]
    for col, typ in [('bank_name','TEXT'),('branch','TEXT'),('ifsc','TEXT'),
                     ('banker_id','TEXT'),('password','TEXT'),
                     ('total_customers','INTEGER DEFAULT 0'),
                     ('approval','INTEGER DEFAULT 0'),
                     ('rejection','INTEGER DEFAULT 0'),
                     ('manual','INTEGER DEFAULT 0')]:
        if col not in bcols:
            c.execute(f"ALTER TABLE bankers ADD COLUMN {col} {typ}")

    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, admin_id TEXT UNIQUE, password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, username TEXT UNIQUE, password TEXT
    )''')
    c.execute("PRAGMA table_info(user_accounts)")
    uacols = [r[1] for r in c.fetchall()]
    if 'password' not in uacols:
        c.execute("ALTER TABLE user_accounts ADD COLUMN password TEXT")

    c.execute('''CREATE TABLE IF NOT EXISTS borrower_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT,
        age INTEGER, email TEXT, address TEXT,
        employment TEXT, employer TEXT,
        aadhar TEXT, pan TEXT,
        purpose TEXT, account_holder TEXT,
        account_number TEXT, ifsc TEXT,
        aadhar_img TEXT, pan_img TEXT, salary_img TEXT, bank_stmt TEXT,
        created_at TEXT
    )''')
    c.execute("PRAGMA table_info(borrower_profiles)")
    bpcols = [r[1] for r in c.fetchall()]
    for col in ['aadhar_img', 'pan_img', 'salary_img', 'bank_stmt']:
        if col not in bpcols:
            c.execute(f"ALTER TABLE borrower_profiles ADD COLUMN {col} TEXT")

    c.execute('''CREATE TABLE IF NOT EXISTS financial_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        income REAL DEFAULT 0,
        total_expense REAL DEFAULT 0,
        transport REAL DEFAULT 0,
        education REAL DEFAULT 0,
        food REAL DEFAULT 0,
        utilities REAL DEFAULT 0,
        other REAL DEFAULT 0,
        risk_score INTEGER DEFAULT 0,
        risk_level TEXT DEFAULT 'New',
        phone TEXT,
        updated_at TEXT
    )''')

    # FIX: correct indentation for user_goals table
    c.execute('''CREATE TABLE IF NOT EXISTS user_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        goal_type TEXT,
        goal_name TEXT,
        target_amount REAL,
        monthly_contribution REAL DEFAULT 0,
        current_savings REAL DEFAULT 0,
        updated_at TEXT
    )''')
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_goal ON user_goals(username, goal_type)")

    c.execute('''CREATE TABLE IF NOT EXISTS loan_expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        expense_id INTEGER,
        cat TEXT,
        amt REAL,
        desc TEXT,
        date TEXT,
        bill TEXT,
        created_at TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def home(): return render_template('index.html')

@app.route('/index')
def index(): return render_template('index.html')

@app.route('/user_dashboard')
def user_dashboard(): return render_template('user_dashboard.html')

@app.route('/banker_dashboard')
def banker_dashboard(): return render_template('banker_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return "Access Denied", 403
    return render_template('admin_dashboard.html')

@app.route('/admin_borrowers')
def admin_borrowers():
    if session.get('role') != 'admin':
        return "Access Denied", 403
    return render_template('admin_borrowers.html')

@app.route('/admin_bankers')
def admin_bankers_page():
    if session.get('role') != 'admin':
        return "Access Denied", 403
    return render_template('admin_bankers.html')

@app.route('/loan_check')
def loan_check(): return render_template('loan_check.html')

@app.route('/financial_advisory')
def financial_advisory(): return render_template('financial_advisory.html')

@app.route('/user_profile')
def user_profile(): return render_template('user_profile.html')

@app.route('/banker_profile')
def banker_profile(): return render_template('banker_profile.html')

@app.route('/admin_profile')
def admin_profile():
    if session.get('role') != 'admin':
        return "Access Denied", 403
    return render_template('admin_profile.html')

@app.route('/banker_review')
def banker_review(): return render_template('banker_review.html')

@app.route('/loan_requests')
def loan_requests(): return render_template('loan_requests.html')

@app.route('/loan_tracking')
def loan_tracking(): return render_template('loan_tracking.html')

@app.route('/apply_loan', methods=['GET'])
def apply_loan_page(): return render_template('apply_loan.html')

# ══════════════════════════════════════════════════════════════════════════════
# SESSION API
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/session', methods=['GET'])
def get_session():
    return jsonify({
        "role":      session.get("role"),
        "username":  session.get("username"),
        "banker_id": session.get("banker_id"),
        "admin_id":  session.get("admin_id"),
        "name":      session.get("name"),
        "phone":     session.get("phone"),
        "email":     session.get("email"),
    })

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

# ══════════════════════════════════════════════════════════════════════════════
# REGISTER
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/register_user', methods=['POST'])
def register_user():
    data     = request.json or {}
    name     = data.get('name', '').strip()
    phone    = normalize_phone(data.get('phone', ''))
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not name or not username or not password:
        return jsonify({"error": "Name, username and password are required."}), 400
    if phone and not validate_phone(phone):
        return jsonify({"error": "Invalid phone number (10 digits, starting 6-9)."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    hashed_pw = generate_password_hash(password)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM user_accounts WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Username already taken."}), 400
    c.execute("INSERT INTO user_accounts (name, phone, username, password) VALUES (?,?,?,?)",
              (name, phone, username, hashed_pw))
    conn.commit()
    conn.close()
    return jsonify({"message": "User registered successfully."})


@app.route('/register_banker', methods=['POST'])
def register_banker():
    data      = request.json or {}
    name      = data.get('name', '').strip()
    banker_id = data.get('banker_id', '').strip()
    bank_name = data.get('bank_name', '').strip()
    branch    = data.get('branch', '').strip() or 'Main Branch'
    ifsc      = data.get('ifsc', '').strip()
    password  = data.get('pass', '').strip()

    if not name or not banker_id or not bank_name or not ifsc or not password:
        return jsonify({"error": "All fields are required."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    hashed_pw = generate_password_hash(password)
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("PRAGMA table_info(bankers)")
        cols = [r[1] for r in c.fetchall()]
        for col, typ in [('bank_name','TEXT'),('branch','TEXT'),('ifsc','TEXT'),
                         ('password','TEXT'),('banker_id','TEXT'),
                         ('total_customers','INTEGER DEFAULT 0'),
                         ('approval','INTEGER DEFAULT 0'),
                         ('rejection','INTEGER DEFAULT 0'),
                         ('manual','INTEGER DEFAULT 0')]:
            if col not in cols:
                c.execute(f"ALTER TABLE bankers ADD COLUMN {col} {typ}")
        conn.commit()
        c.execute("SELECT id FROM bankers WHERE banker_id=?", (banker_id,))
        if c.fetchone():
            conn.close()
            return jsonify({"error": "Banker ID already registered."}), 400
        c.execute('''INSERT INTO bankers
                     (name, bank_name, branch, ifsc, banker_id, password,
                      total_customers, approval, rejection, manual)
                     VALUES (?,?,?,?,?,?,0,0,0,0)''',
                  (name, bank_name, branch, ifsc, banker_id, hashed_pw))
        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({"error": "Registration error: " + str(e)}), 500
    return jsonify({"message": "Banker registered successfully."})


@app.route('/register_admin', methods=['POST'])
def register_admin():
    return jsonify({"error": "Admin registration is disabled."}), 403

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/login_user', methods=['POST'])
def login_user():
    data     = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Enter all fields!"}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, name, phone, password FROM user_accounts WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Username not found. Please register first."}), 404

    stored_pw = row[3] or ''
    pw_ok = (check_password_hash(stored_pw, password)
             if stored_pw.startswith('pbkdf2:') or stored_pw.startswith('scrypt:')
             else stored_pw == password)
    if not pw_ok:
        return jsonify({"error": "Wrong password!"}), 401

    session.clear()
    session.permanent   = True
    session['role']     = 'user'
    session['username'] = username
    session['name']     = row[1]
    session['phone']    = normalize_phone(row[2] or '')
    return jsonify({"message": "Login successful.", "name": row[1], "username": username})


@app.route('/login_banker', methods=['POST'])
def login_banker():
    data      = request.json or {}
    banker_id = data.get('banker_id', '').strip()
    password  = data.get('password', '').strip()

    if not banker_id or not password:
        return jsonify({"error": "Enter all fields!"}), 400

    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("PRAGMA table_info(bankers)")
        cols = [r[1] for r in c.fetchall()]
        for col, typ in [('bank_name','TEXT'),('branch','TEXT'),('ifsc','TEXT'),
                         ('password','TEXT'),('banker_id','TEXT'),
                         ('total_customers','INTEGER DEFAULT 0'),
                         ('approval','INTEGER DEFAULT 0'),
                         ('rejection','INTEGER DEFAULT 0'),
                         ('manual','INTEGER DEFAULT 0')]:
            if col not in cols:
                c.execute(f"ALTER TABLE bankers ADD COLUMN {col} {typ}")
        conn.commit()
        c.execute("SELECT id, name, bank_name, password FROM bankers WHERE banker_id=?", (banker_id,))
        row = c.fetchone()
        conn.close()
    except Exception as e:
        return jsonify({"error": "Login error: " + str(e)}), 500

    if not row:
        return jsonify({"error": "Banker ID not found. Please register first."}), 404

    stored_pw = row[3] or ''
    if not stored_pw:
        return jsonify({"error": "No password set. Please re-register."}), 401
    pw_ok = (check_password_hash(stored_pw, password)
             if stored_pw.startswith('pbkdf2:') or stored_pw.startswith('scrypt:')
             else stored_pw == password)
    if not pw_ok:
        return jsonify({"error": "Wrong password!"}), 401

    session.clear()
    session.permanent    = True
    session['role']      = 'banker'
    session['banker_id'] = banker_id
    session['name']      = row[1]
    return jsonify({"message": "Login successful.", "name": row[1], "banker_id": banker_id})


@app.route('/login_admin', methods=['POST'])
def login_admin():
    data     = request.json or {}
    admin_id = data.get('admin_id', '').strip()
    password = data.get('password', '').strip()

    if not admin_id or not password:
        return jsonify({"error": "Enter all fields!"}), 400

    if admin_id != ADMIN_ID or password != ADMIN_PASSWORD:
        return jsonify({"error": "Access Denied"}), 401

    session.clear()
    session.permanent   = True
    session['role']     = 'admin'
    session['admin_id'] = ADMIN_ID
    session['name']     = ADMIN_NAME
    session['email']    = ADMIN_EMAIL
    return jsonify({"message": "Login successful.", "name": ADMIN_NAME, "admin_id": ADMIN_ID})


@app.route('/check_username', methods=['POST'])
def check_username():
    username = (request.json or {}).get('username', '').strip()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM user_accounts WHERE username=?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return jsonify({"exists": exists})

# ══════════════════════════════════════════════════════════════════════════════
# FINANCIAL DATA
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/financial_data', methods=['GET'])
def get_financial_data():
    username = session.get('username') or request.args.get('username', '').strip()
    if not username:
        return jsonify({"error": "Not logged in"}), 401

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM financial_data WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()

    if row:
        cols = ['id', 'username', 'income', 'total_expense', 'transport', 'education',
                'food', 'utilities', 'other', 'risk_score', 'risk_level', 'phone', 'updated_at']
        return jsonify(dict(zip(cols, row)))
    return jsonify({"username": username, "income": 0, "total_expense": 0, "transport": 0,
                    "education": 0, "food": 0, "utilities": 0, "other": 0,
                    "risk_score": None, "risk_level": None, "phone": "", "updated_at": ""})


@app.route('/api/financial_data', methods=['POST'])
def save_financial_data():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 401

    data          = request.json or {}
    income        = data.get('income', 0)
    total_expense = data.get('total_expense', 0)
    transport     = data.get('transport', 0)
    education     = data.get('education', 0)
    food          = data.get('food', 0)
    utilities     = data.get('utilities', 0)
    other         = data.get('other', 0)
    phone         = normalize_phone(data.get('phone', ''))
    updated_at    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_risk_score = data.get('risk_score')
    new_risk_level = data.get('risk_level')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, risk_score, risk_level FROM financial_data WHERE username=?", (username,))
    row = c.fetchone()

    if row:
        risk_score = new_risk_score if new_risk_score is not None else row[1]
        risk_level = new_risk_level if new_risk_level is not None else row[2]
        c.execute('''UPDATE financial_data
                     SET income=?, total_expense=?, transport=?, education=?,
                         food=?, utilities=?, other=?,
                         risk_score=?, risk_level=?, phone=?, updated_at=?
                     WHERE username=?''',
                  (income, total_expense, transport, education, food, utilities, other,
                   risk_score, risk_level, phone, updated_at, username))
    else:
        risk_score = new_risk_score if new_risk_score is not None else 0
        risk_level = new_risk_level if new_risk_level is not None else 'New'
        c.execute('''INSERT INTO financial_data
                     (username, income, total_expense, transport, education,
                      food, utilities, other, risk_score, risk_level, phone, updated_at)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (username, income, total_expense, transport, education,
                   food, utilities, other, risk_score, risk_level, phone, updated_at))

    if phone:
        c.execute("UPDATE user_accounts SET phone=? WHERE username=?", (phone, username))
        session['phone'] = phone

    conn.commit()
    conn.close()
    return jsonify({"message": "Financial data saved."})


@app.route('/api/user_goals', methods=['GET'])
def get_user_goals():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""SELECT goal_type, goal_name, target_amount, monthly_contribution, current_savings
                 FROM user_goals WHERE username=?""", (username,))
    rows = c.fetchall()
    conn.close()
    goals = {}
    for r in rows:
        goals[r[0]] = {"name": r[1] or "", "target": float(r[2] or 0),
                       "monthly": float(r[3] or 0), "current": float(r[4] or 0)}
    return jsonify(goals)


@app.route('/api/user_goals', methods=['POST'])
def save_user_goals():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    data = request.json or {}
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM user_goals WHERE username=?", (username,))
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for goal_type, g in data.items():
        if isinstance(g, dict) and g.get('target', 0) > 0:
            c.execute('''INSERT INTO user_goals
                         (username, goal_type, goal_name, target_amount,
                          monthly_contribution, current_savings, updated_at)
                         VALUES (?,?,?,?,?,?,?)''',
                      (username, goal_type, g.get('name',''), g.get('target',0),
                       g.get('monthly',0), g.get('current',0), current_time))
    conn.commit()
    conn.close()
    return jsonify({"message": "Goals saved successfully"})

# ══════════════════════════════════════════════════════════════════════════════
# LOAN EXPENSES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/loan_expenses', methods=['GET'])
def get_loan_expenses():
    username = session.get('username') or request.args.get('username', '').strip()
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''SELECT id, expense_id, cat, amt, desc, date, bill, created_at
                 FROM loan_expenses WHERE username=? ORDER BY date DESC''', (username,))
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id": r[1], "cat": r[2], "amt": r[3], "desc": r[4],
                     "date": r[5], "bill": r[6], "created_at": r[7]} for r in rows])


@app.route('/api/loan_expenses', methods=['POST'])
def add_loan_expense():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    data       = request.json or {}
    expense_id = data.get('id', int(datetime.now().timestamp() * 1000))
    cat        = data.get('cat', '')
    amt        = data.get('amt', 0)
    desc       = data.get('desc', '')
    date       = data.get('date', '')
    bill       = data.get('bill', None)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''INSERT INTO loan_expenses
                 (username, expense_id, cat, amt, desc, date, bill, created_at)
                 VALUES (?,?,?,?,?,?,?,?)''',
              (username, expense_id, cat, amt, desc, date, bill,
               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense saved.", "id": expense_id})


@app.route('/api/loan_expenses/<int:expense_id>', methods=['DELETE'])
def delete_loan_expense(expense_id):
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM loan_expenses WHERE username=? AND expense_id=?", (username, expense_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

# ══════════════════════════════════════════════════════════════════════════════
# USER PROFILE UPDATE
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/update_user_profile', methods=['POST'])
def update_user_profile():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    data         = request.json or {}
    new_name     = data.get('name', '').strip()
    new_phone    = normalize_phone(data.get('phone', ''))
    new_username = data.get('username', '').strip()

    if new_phone and not validate_phone(new_phone):
        return jsonify({"error": "Invalid phone number."}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    if new_username and new_username != username:
        c.execute("SELECT id FROM user_accounts WHERE username=?", (new_username,))
        if c.fetchone():
            conn.close()
            return jsonify({"error": "Username already taken."}), 400
        c.execute("UPDATE financial_data SET username=? WHERE username=?", (new_username, username))
        c.execute("UPDATE loan_expenses   SET username=? WHERE username=?", (new_username, username))
        c.execute("UPDATE user_accounts SET username=?, name=?, phone=? WHERE username=?",
                  (new_username, new_name, new_phone, username))
        session['username'] = new_username
    else:
        c.execute("UPDATE user_accounts SET name=?, phone=? WHERE username=?",
                  (new_name, new_phone, username))
    session['name']  = new_name
    session['phone'] = new_phone
    conn.commit()
    conn.close()
    return jsonify({"message": "Profile updated.", "username": session['username']})

# ══════════════════════════════════════════════════════════════════════════════
# APPLY LOAN — FIX: restored original response format that apply_loan.html expects
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/apply_loan', methods=['POST'])
def apply_loan():
    data       = request.json or {}
    name       = (data.get('name') or '').strip()
    phone      = normalize_phone(data.get('phone') or '')
    age        = data.get('age', 0)
    loanAmount = data.get('loanAmount')
    loanType   = data.get('loanType')
    tenure     = data.get('tenure')
    emi        = data.get('emi')
    risk_score = data.get('risk_score')

    if not name:
        return jsonify({"error": "Name is required."}), 400
    if not validate_phone(phone):
        return jsonify({"error": "Invalid phone number."}), 400
    if not validate_loan_amount(loanAmount):
        return jsonify({"error": "Loan amount must be between Rs.1,000 and Rs.1,00,00,000."}), 400
    if not validate_tenure(tenure):
        return jsonify({"error": "Tenure must be between 1 and 360 months."}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM bankers")
    banker_count = c.fetchone()[0]
    try:
        c.execute('''INSERT INTO users
                     (name, age, phone, loanAmount, loanType, tenure, emi,
                      risk_score, allocated_banker, loan_status, reason, created_at)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (name, age, phone, loanAmount, loanType, tenure, emi,
                   risk_score, None, "Pending", "",
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500
    conn.close()
    # FIX: return original format that apply_loan.html expects
    return jsonify({"message": "no_banker" if banker_count == 0 else "submitted"})

# ══════════════════════════════════════════════════════════════════════════════
# PICKUP LOAN
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/pickup_loan', methods=['POST'])
def pickup_loan():
    data        = request.json or {}
    user_id     = data.get('user_id')
    banker_name = data.get('banker_name', '').strip()

    if not user_id or not banker_name:
        return jsonify({"error": "Missing data."}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("BEGIN IMMEDIATE")
        c.execute("SELECT allocated_banker FROM users WHERE id=?", (user_id,))
        row = c.fetchone()
        if not row:
            conn.rollback(); conn.close()
            return jsonify({"error": "Application not found."}), 404
        if row[0]:
            conn.rollback(); conn.close()
            return jsonify({"error": "Already picked up by another banker."}), 400
        c.execute("UPDATE users SET allocated_banker=?, loan_status=? WHERE id=?",
                  (banker_name, "Picked Up", user_id))
        conn.commit()
    except Exception as e:
        conn.rollback(); conn.close()
        return jsonify({"error": f"Could not pick up: {str(e)}"}), 500
    conn.close()
    return jsonify({"message": "Picked up successfully."})

# ══════════════════════════════════════════════════════════════════════════════
# BANKER ACTION
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/banker_action', methods=['POST'])
def banker_action():
    data    = request.json or {}
    user_id = data.get('user_id')
    action  = data.get('action')
    reason  = data.get('reason', '')

    VALID_ACTIONS = ("Approved", "Rejected", "Manual Review", "Picked Up", "Pending")
    if action not in VALID_ACTIONS:
        return jsonify({"error": f"Invalid action '{action}'."}), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT loan_status, allocated_banker FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    current_status, banker = row[0], row[1]
    c.execute("UPDATE users SET loan_status=?, reason=? WHERE id=?", (action, reason, user_id))

    if banker:
        first_action = current_status in ("Pending", "Picked Up")
        if current_status == "Approved" and action != "Approved":
            c.execute("UPDATE bankers SET approval=CASE WHEN approval>0 THEN approval-1 ELSE 0 END WHERE name=?", (banker,))
        elif current_status == "Rejected" and action != "Rejected":
            c.execute("UPDATE bankers SET rejection=CASE WHEN rejection>0 THEN rejection-1 ELSE 0 END WHERE name=?", (banker,))
        elif current_status == "Manual Review" and action != "Manual Review":
            c.execute("UPDATE bankers SET manual=CASE WHEN manual>0 THEN manual-1 ELSE 0 END WHERE name=?", (banker,))
        if action == "Approved":
            c.execute("UPDATE bankers SET approval=approval+1 WHERE name=?", (banker,))
        elif action == "Rejected":
            c.execute("UPDATE bankers SET rejection=rejection+1 WHERE name=?", (banker,))
        elif action == "Manual Review":
            c.execute("UPDATE bankers SET manual=manual+1 WHERE name=?", (banker,))
        if first_action:
            c.execute("UPDATE bankers SET total_customers=total_customers+1 WHERE name=?", (banker,))

    conn.commit()
    conn.close()
    return jsonify({"message": "Action recorded"})

# ══════════════════════════════════════════════════════════════════════════════
# GET STATUS — FIX: safe row variable, phone + name fallback
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/get_status/<phone>')
def get_status(phone):
    phone = normalize_phone(phone)
    name  = request.args.get('name', '').strip()
    row   = None  # FIX: always initialize row to avoid NameError

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if phone:
        c.execute('''SELECT loan_status, reason, allocated_banker, created_at
                     FROM users WHERE phone=? ORDER BY id DESC LIMIT 1''', (phone,))
        row = c.fetchone()

    if not row and name:
        c.execute('''SELECT loan_status, reason, allocated_banker, created_at
                     FROM users WHERE name=? ORDER BY id DESC LIMIT 1''', (name,))
        row = c.fetchone()

    conn.close()

    if row:
        return jsonify({"status": row[0], "reason": row[1] or "",
                        "banker": row[2] or "", "created_at": row[3] or ""})
    return jsonify({"status": "No Application", "reason": "", "banker": "", "created_at": ""})

# ══════════════════════════════════════════════════════════════════════════════
# USERS / BANKERS / STATS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/users')
def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id,name,age,phone,loanAmount,loanType,tenure,emi,risk_score,allocated_banker,loan_status,reason FROM users")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"age":r[2],"phone":r[3],
                     "loanAmount":r[4],"loanType":r[5],"tenure":r[6],
                     "emi":r[7],"score":r[8],"banker":r[9],
                     "status":r[10],"reason":r[11]} for r in rows])


@app.route('/users')
def api_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id,name,phone,loanAmount,loanType,tenure,emi,risk_score,allocated_banker,loan_status,reason FROM users")
    rows = c.fetchall()
    conn.close()
    return jsonify([[r[0],r[1] or "",r[2] or "",r[3] or 0,r[4] or "",
                     r[5] or 0,r[6] or 0,r[7] or 0,r[8] or "",
                     r[9] or "Pending",r[10] or ""] for r in rows])


@app.route('/api/bankers')
def get_bankers():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bankers)")
    cols = [col[1] for col in c.fetchall()]
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    conn.close()
    result = []
    for b in rows:
        r = dict(zip(cols, b))
        result.append({"id":r.get("id",""),"name":r.get("name",""),
                        "bankName":r.get("bank_name",""),"branch":r.get("branch",""),
                        "ifsc":r.get("ifsc",""),"bankerId":r.get("banker_id",""),
                        "totalCustomers":r.get("total_customers",0),
                        "approval":r.get("approval",0),"rejection":r.get("rejection",0),
                        "manual":r.get("manual",0)})
    return jsonify(result)


@app.route('/api/banks')
def get_banks():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bankers)")
    cols = [col[1] for col in c.fetchall()]
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    conn.close()
    seen, banks = set(), []
    for r in rows:
        row = dict(zip(cols, r))
        k = row.get("bank_name","")
        if k not in seen:
            seen.add(k)
            banks.append({"name":k,"branch":row.get("branch",""),"ifsc":row.get("ifsc","")})
    return jsonify(banks)


@app.route('/api/get_banker/<banker_id>')
def get_banker_by_id(banker_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bankers)")
    cols = [col[1] for col in c.fetchall()]
    c.execute("SELECT * FROM bankers WHERE banker_id=?", (banker_id,))
    row = c.fetchone()
    if not row:
        c.execute("SELECT * FROM bankers WHERE name=?", (banker_id,))
        row = c.fetchone()
    conn.close()
    if row:
        r = dict(zip(cols, row))
        return jsonify({"name":r.get("name",""),"bankName":r.get("bank_name",""),
                        "ifsc":r.get("ifsc",""),"branch":r.get("branch",""),
                        "bankerId":r.get("banker_id","")})
    return jsonify({"error": "Not found"}), 404


@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_loans = c.fetchone()[0]
    c.execute("SELECT loan_status, COUNT(*) FROM users GROUP BY loan_status")
    status_counts = dict(c.fetchall())
    c.execute("SELECT COUNT(*) FROM bankers")
    total_bankers = c.fetchone()[0]
    c.execute("SELECT SUM(total_customers),SUM(approval),SUM(rejection),SUM(manual) FROM bankers")
    bt = c.fetchone()
    conn.close()
    return jsonify({"total_loans":total_loans,"status_counts":status_counts,
                    "total_bankers":total_bankers,"total_customers":bt[0] or 0,
                    "total_approved":bt[1] or 0,"total_rejected":bt[2] or 0,
                    "total_manual_review":bt[3] or 0})

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN-ONLY APIs
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/borrowers')
def api_borrowers():
    if session.get('role') != 'admin':
        return jsonify({"error": "Access Denied"}), 403
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"age":r[2],"phone":r[3],
                     "loanAmount":r[4],"loanType":r[5],"tenure":r[6],
                     "emi":r[7],"risk_score":r[8],"allocated_banker":r[9],
                     "loan_status":r[10],"reason":r[11]} for r in rows])


@app.route('/api/admin_bankers')
def api_admin_bankers():
    if session.get('role') != 'admin':
        return jsonify({"error": "Access Denied"}), 403
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bankers)")
    cols = [col[1] for col in c.fetchall()]
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    conn.close()
    result = []
    for b in rows:
        r = dict(zip(cols, b))
        result.append({"id":r.get("id",""),"name":r.get("name",""),
                        "bank_name":r.get("bank_name",""),"branch":r.get("branch",""),
                        "ifsc":r.get("ifsc",""),"banker_id":r.get("banker_id",""),
                        "total_customers":r.get("total_customers",0),
                        "approval":r.get("approval",0),"rejection":r.get("rejection",0),
                        "manual":r.get("manual",0)})
    return jsonify(result)


@app.route('/api/user_accounts')
def get_user_accounts():
    if session.get('role') != 'admin':
        return jsonify({"error": "Access Denied"}), 403
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_accounts")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"phone":r[2],"username":r[3]} for r in rows])


@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    if session.get('role') != 'admin':
        return jsonify({"error": "Access Denied"}), 403
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})


@app.route('/reset_all', methods=['POST'])
def reset_all():
    if session.get('role') != 'admin':
        return jsonify({"error": "Access Denied"}), 403
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users")
    c.execute("DELETE FROM bankers")
    conn.commit()
    conn.close()
    return jsonify({"message": "Reset successful"})


@app.route('/update_status', methods=['POST'])
def update_status():
    if session.get('role') != 'admin':
        return jsonify({"error": "Access Denied"}), 403
    data = request.json or {}
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET loan_status=?, reason=? WHERE id=?",
              (data['status'], data['reason'], data['id']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})


@app.route('/save', methods=['POST'])
def save_data():
    data = request.json or {}
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name, phone, loan_status, reason) VALUES (?,?,?,?)",
              (data.get('name'), data.get('phone'), "Pending", ""))
    conn.commit()
    conn.close()
    return jsonify({"message": "Saved"})


@app.route('/admin_remove_banker/<int:id>', methods=['DELETE'])
def admin_remove_banker(id):
    if session.get('role') != 'admin':
        return jsonify({"error": "Access Denied"}), 403
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name FROM bankers WHERE id=?", (id,))
    row = c.fetchone()
    if row:
        c.execute("""UPDATE users SET allocated_banker=NULL, loan_status='Pending'
                     WHERE allocated_banker=? AND loan_status NOT IN ('Approved','Rejected')""", (row[0],))
    c.execute("DELETE FROM bankers WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Banker removed"})

# ══════════════════════════════════════════════════════════════════════════════
# BORROWER PROFILE
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/save_borrower_profile', methods=['POST'])
def save_borrower_profile():
    is_multipart = request.content_type and 'multipart/form-data' in request.content_type
    if is_multipart:
        form = request.form; files = request.files
        def fget(k, default=''): return form.get(k, default)
    else:
        form = request.json or {}; files = {}
        def fget(k, default=''): return form.get(k, default)

    phone = normalize_phone(fget('phone', ''))
    name  = fget('name', '').strip()
    if not phone:
        return jsonify({"error": "Phone number is required."}), 400

    conn = sqlite3.connect('users.db')
    cur  = conn.cursor()
    cur.execute("PRAGMA table_info(borrower_profiles)")
    existing_cols = [r[1] for r in cur.fetchall()]
    for col in ['aadhar_img','pan_img','salary_img','bank_stmt']:
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE borrower_profiles ADD COLUMN {col} TEXT")

    cur.execute("SELECT id,aadhar_img,pan_img,salary_img,bank_stmt FROM borrower_profiles WHERE phone=?", (phone,))
    existing_row = cur.fetchone()
    existing_imgs = {
        'aadhar_img': existing_row[1] if existing_row else None,
        'pan_img':    existing_row[2] if existing_row else None,
        'salary_img': existing_row[3] if existing_row else None,
        'bank_stmt':  existing_row[4] if existing_row else None,
    }

    def save_upload(field_name, json_alias, existing_path):
        f = files.get(field_name) if is_multipart else None
        if f and f.filename:
            if not allowed_file(f.filename):
                return None, f"Invalid file type for {field_name}."
            ext = f.filename.rsplit('.',1)[1].lower()
            filename = secure_filename(f"{phone}_{field_name}_{int(datetime.now().timestamp())}.{ext}")
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            return f"uploads/{filename}", None
        return fget(json_alias) or fget(field_name) or existing_path, None

    errors = []
    aadhar_img, err = save_upload('aadhar_img','aadharImg',existing_imgs['aadhar_img']); err and errors.append(err)
    pan_img,    err = save_upload('pan_img','panImg',existing_imgs['pan_img']);           err and errors.append(err)
    salary_img, err = save_upload('salary_img','salaryImg',existing_imgs['salary_img']); err and errors.append(err)
    bank_stmt,  err = save_upload('bank_stmt','bankStmt',existing_imgs['bank_stmt']);    err and errors.append(err)
    if errors:
        conn.close()
        return jsonify({"error": " | ".join(errors)}), 400

    update_vals = (name, fget('age',0), fget('email',''), fget('address',''),
                   fget('employment',''), fget('employer',''), fget('aadhar',''),
                   fget('pan',''), fget('purpose',''), fget('accountHolder',''),
                   fget('accountNumber',''), fget('ifsc',''),
                   aadhar_img, pan_img, salary_img, bank_stmt)

    if existing_row:
        cur.execute('''UPDATE borrower_profiles SET name=?,age=?,email=?,address=?,employment=?,employer=?,
                       aadhar=?,pan=?,purpose=?,account_holder=?,account_number=?,ifsc=?,
                       aadhar_img=?,pan_img=?,salary_img=?,bank_stmt=? WHERE phone=?''',
                    update_vals + (phone,))
    else:
        cur.execute('''INSERT INTO borrower_profiles (name,phone,age,email,address,employment,employer,
                       aadhar,pan,purpose,account_holder,account_number,ifsc,
                       aadhar_img,pan_img,salary_img,bank_stmt,created_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (name, phone) + update_vals[1:] + (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
    conn.commit()
    conn.close()
    return jsonify({"message": "saved"})


@app.route('/api/borrower_profile')
def get_borrower_profile():
    phone = normalize_phone(request.args.get('phone',''))
    name  = request.args.get('name','').strip()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    row = None
    if phone and name:
        c.execute("SELECT * FROM borrower_profiles WHERE phone=? AND name=? LIMIT 1", (phone, name))
        row = c.fetchone()
    if not row and phone:
        c.execute("SELECT * FROM borrower_profiles WHERE phone=? LIMIT 1", (phone,))
        row = c.fetchone()
    if not row and name:
        c.execute("SELECT * FROM borrower_profiles WHERE name=? LIMIT 1", (name,))
        row = c.fetchone()
    c.execute("PRAGMA table_info(borrower_profiles)")
    cols = [r[1] for r in c.fetchall()]
    conn.close()
    if row:
        return jsonify(dict(zip(cols, row)))
    return jsonify({"error": "not found"}), 404


@app.route('/static/sw.js')
def service_worker():
    from flask import send_from_directory, make_response
    resp = make_response(send_from_directory('static', 'sw.js'))
    resp.headers['Content-Type'] = 'application/javascript'
    resp.headers['Service-Worker-Allowed'] = '/'
    return resp

# ══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ══════════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):      return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):   return render_template('500.html'), 500

@app.errorhandler(413)
def file_too_large(e): return jsonify({"error": "File too large. Max 5MB."}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5050)))
