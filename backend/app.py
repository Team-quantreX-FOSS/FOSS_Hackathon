from flask import Flask, render_template, request, jsonify, session
import sqlite3
from datetime import datetime
import secrets

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'finrisk_secret_key_2024_xk9z'

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
    if 'password' not in bcols:
        c.execute("ALTER TABLE bankers ADD COLUMN password TEXT")

    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, admin_id TEXT UNIQUE, password TEXT
    )''')
    c.execute("PRAGMA table_info(admins)")
    acols = [r[1] for r in c.fetchall()]
    if 'password' not in acols:
        c.execute("ALTER TABLE admins ADD COLUMN password TEXT")

    c.execute('''CREATE TABLE IF NOT EXISTS user_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, username TEXT UNIQUE, password TEXT
    )''')
    c.execute("PRAGMA table_info(user_accounts)")
    ucols = [r[1] for r in c.fetchall()]
    if 'password' not in ucols:
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
    for col in ['aadhar_img','pan_img','salary_img','bank_stmt']:
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

# PAGE ROUTES
@app.route('/')
def home(): return render_template('index.html')
@app.route('/index')
def index(): return render_template('index.html')
@app.route('/user_dashboard')
def user_dashboard(): return render_template('user_dashboard.html')
@app.route('/banker_dashboard')
def banker_dashboard(): return render_template('banker_dashboard.html')
@app.route('/admin_dashboard')
def admin_dashboard(): return render_template('admin_dashboard.html')
@app.route('/admin_borrowers')
def admin_borrowers(): return render_template('admin_borrowers.html')
@app.route('/admin_bankers')
def admin_bankers(): return render_template('admin_bankers.html')
@app.route('/loan_check')
def loan_check(): return render_template('loan_check.html')
@app.route('/financial_advisory')
def financial_advisory(): return render_template('financial_advisory.html')
@app.route('/user_profile')
def user_profile(): return render_template('user_profile.html')
@app.route('/banker_profile')
def banker_profile(): return render_template('banker_profile.html')
@app.route('/admin_profile')
def admin_profile(): return render_template('admin_profile.html')
@app.route('/banker_review')
def banker_review(): return render_template('banker_review.html')
@app.route('/loan_requests')
def loan_requests(): return render_template('loan_requests.html')
@app.route('/loan_tracking')
def loan_tracking(): return render_template('loan_tracking.html')
@app.route('/apply_loan', methods=['GET'])
def apply_loan_page(): return render_template('apply_loan.html')

# SESSION API
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

# REGISTER
@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.json
    name = data.get('name','').strip()
    phone = data.get('phone','').strip()
    username = data.get('username','').strip()
    password = data.get('password','').strip()
    if not name or not username or not password:
        return jsonify({"error": "Name, username and password are required."}), 400
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM user_accounts WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Username already taken."}), 400
    c.execute("INSERT INTO user_accounts (name,phone,username,password) VALUES (?,?,?,?)",
              (name, phone, username, password))
    conn.commit()
    conn.close()
    return jsonify({"message": "User registered successfully."})

@app.route('/register_banker', methods=['POST'])
def register_banker():
    data = request.json
    name = data.get('name','').strip()
    banker_id = data.get('banker_id','').strip()
    bank_name = data.get('bank_name','').strip()
    branch = data.get('branch','').strip()
    ifsc = data.get('ifsc','').strip()
    password = data.get('pass','').strip()
    if not name or not banker_id or not bank_name or not ifsc or not password:
        return jsonify({"error": "All fields are required."}), 400
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM bankers WHERE banker_id=?", (banker_id,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Banker ID already registered."}), 400
    c.execute('INSERT INTO bankers (name,bank_name,branch,ifsc,banker_id,password,total_customers,approval,rejection,manual) VALUES (?,?,?,?,?,?,0,0,0,0)',
              (name, bank_name, branch, ifsc, banker_id, password))
    conn.commit()
    conn.close()
    return jsonify({"message": "Banker registered successfully."})

@app.route('/register_admin', methods=['POST'])
def register_admin():
    data = request.json
    name = data.get('name','').strip()
    email = data.get('email','').strip()
    admin_id = data.get('admin_id','').strip()
    password = data.get('pass','').strip()
    if not name or not email or not admin_id or not password:
        return jsonify({"error": "All fields are required."}), 400
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM admins WHERE admin_id=?", (admin_id,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "Admin ID already exists."}), 400
    c.execute("INSERT INTO admins (name,email,admin_id,password) VALUES (?,?,?,?)",
              (name, email, admin_id, password))
    conn.commit()
    conn.close()
    return jsonify({"message": "Admin registered successfully."})

# LOGIN
@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username','').strip()
    password = data.get('password','').strip()
    if not username or not password:
        return jsonify({"error": "Enter all fields!"}), 400
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id,name,phone,password FROM user_accounts WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Username not found. Please register first."}), 404
    if row[3] != password:
        return jsonify({"error": "Wrong password!"}), 401
    session.clear()
    session['role'] = 'user'
    session['username'] = username
    session['name'] = row[1]
    session['phone'] = row[2] or ''
    return jsonify({"message": "Login successful.", "name": row[1], "username": username})

@app.route('/login_banker', methods=['POST'])
def login_banker():
    data = request.json
    banker_id = data.get('banker_id','').strip()
    password = data.get('password','').strip()
    if not banker_id or not password:
        return jsonify({"error": "Enter all fields!"}), 400
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id,name,bank_name,password FROM bankers WHERE banker_id=?", (banker_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Banker ID not found. Please register first."}), 404
    if row[3] != password:
        return jsonify({"error": "Wrong password!"}), 401
    session.clear()
    session['role'] = 'banker'
    session['banker_id'] = banker_id
    session['name'] = row[1]
    return jsonify({"message": "Login successful.", "name": row[1], "banker_id": banker_id})

@app.route('/login_admin', methods=['POST'])
def login_admin():
    data = request.json
    admin_id = data.get('admin_id','').strip()
    password = data.get('password','').strip()
    if not admin_id or not password:
        return jsonify({"error": "Enter all fields!"}), 400
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id,name,email,password FROM admins WHERE admin_id=?", (admin_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Admin ID not found. Please register first."}), 404
    if row[3] != password:
        return jsonify({"error": "Wrong password!"}), 401
    session.clear()
    session['role'] = 'admin'
    session['admin_id'] = admin_id
    session['name'] = row[1]
    session['email'] = row[2]
    return jsonify({"message": "Login successful.", "name": row[1], "admin_id": admin_id})

@app.route('/check_username', methods=['POST'])
def check_username():
    username = request.json.get('username','').strip()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM user_accounts WHERE username=?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return jsonify({"exists": exists})

# FINANCIAL DATA
@app.route('/api/financial_data', methods=['GET'])
def get_financial_data():
    username = session.get('username') or request.args.get('username','').strip()
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM financial_data WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        cols = ['id','username','income','total_expense','transport','education',
                'food','utilities','other','risk_score','risk_level','phone','updated_at']
        return jsonify(dict(zip(cols, row)))
    return jsonify({"username":username,"income":0,"total_expense":0,"transport":0,
                    "education":0,"food":0,"utilities":0,"other":0,
                    "risk_score":None,"risk_level":None,"phone":"","updated_at":""})

@app.route('/api/financial_data', methods=['POST'])
def save_financial_data():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 401

    data          = request.json
    income        = data.get('income', 0)
    total_expense = data.get('total_expense', 0)
    transport     = data.get('transport', 0)
    education     = data.get('education', 0)
    food          = data.get('food', 0)
    utilities     = data.get('utilities', 0)
    other         = data.get('other', 0)
    phone         = data.get('phone', '')
    updated_at    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Only update risk fields if they are explicitly provided (not null/None)
    # This prevents the financial details popup from wiping out eligibility results
    new_risk_score = data.get('risk_score')   # stays None if not sent or sent as null
    new_risk_level = data.get('risk_level')   # stays None if not sent or sent as null

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, risk_score, risk_level FROM financial_data WHERE username=?", (username,))
    row = c.fetchone()

    if row:
        # Row exists — preserve existing risk values unless new ones are given
        existing_risk_score = row[1]  # could be 0, an int, or None
        existing_risk_level = row[2]  # could be 'New', a string, or None

        risk_score = new_risk_score if new_risk_score is not None else existing_risk_score
        risk_level = new_risk_level if new_risk_level is not None else existing_risk_level

        c.execute('''UPDATE financial_data
                     SET income=?, total_expense=?, transport=?, education=?,
                         food=?, utilities=?, other=?,
                         risk_score=?, risk_level=?, phone=?, updated_at=?
                     WHERE username=?''',
                  (income, total_expense, transport, education, food, utilities, other,
                   risk_score, risk_level, phone, updated_at, username))
    else:
        # New record — use provided values or sensible defaults
        risk_score = new_risk_score if new_risk_score is not None else 0
        risk_level = new_risk_level if new_risk_level is not None else 'New'

        c.execute('''INSERT INTO financial_data
                     (username, income, total_expense, transport, education, food, utilities, other,
                      risk_score, risk_level, phone, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (username, income, total_expense, transport, education, food, utilities, other,
                   risk_score, risk_level, phone, updated_at))

    if phone:
        c.execute("UPDATE user_accounts SET phone=? WHERE username=?", (phone, username))
        session['phone'] = phone

    conn.commit()
    conn.close()
    return jsonify({"message": "Financial data saved."})

# LOAN EXPENSES
@app.route('/api/loan_expenses', methods=['GET'])
def get_loan_expenses():
    username = session.get('username') or request.args.get('username','').strip()
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id,expense_id,cat,amt,desc,date,bill,created_at FROM loan_expenses WHERE username=? ORDER BY date DESC', (username,))
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":r[1],"cat":r[2],"amt":r[3],"desc":r[4],"date":r[5],"bill":r[6],"created_at":r[7]} for r in rows])

@app.route('/api/loan_expenses', methods=['POST'])
def add_loan_expense():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    data = request.json
    expense_id = data.get('id', int(datetime.now().timestamp()*1000))
    cat = data.get('cat','')
    amt = data.get('amt',0)
    desc = data.get('desc','')
    date = data.get('date','')
    bill = data.get('bill',None)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO loan_expenses (username,expense_id,cat,amt,desc,date,bill,created_at) VALUES (?,?,?,?,?,?,?,?)',
              (username, expense_id, cat, amt, desc, date, bill, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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

# USER PROFILE UPDATE
@app.route('/api/update_user_profile', methods=['POST'])
def update_user_profile():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    data = request.json
    new_name = data.get('name','').strip()
    new_phone = data.get('phone','').strip()
    new_username = data.get('username','').strip()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    if new_username and new_username != username:
        c.execute("SELECT id FROM user_accounts WHERE username=?", (new_username,))
        if c.fetchone():
            conn.close()
            return jsonify({"error": "Username already taken."}), 400
        c.execute("UPDATE financial_data SET username=? WHERE username=?", (new_username, username))
        c.execute("UPDATE loan_expenses SET username=? WHERE username=?", (new_username, username))
        c.execute("UPDATE user_accounts SET username=?,name=?,phone=? WHERE username=?",
                  (new_username, new_name, new_phone, username))
        session['username'] = new_username
    else:
        c.execute("UPDATE user_accounts SET name=?,phone=? WHERE username=?", (new_name, new_phone, username))
    session['name'] = new_name
    session['phone'] = new_phone
    conn.commit()
    conn.close()
    return jsonify({"message": "Profile updated.", "username": session['username']})

# APPLY LOAN
@app.route('/apply_loan', methods=['POST'])
def apply_loan():
    data = request.json
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(users)")
    existing = [r[1] for r in c.fetchall()]
    for col, typ in [("address","TEXT"),("employment","TEXT"),("purpose","TEXT"),("aadhar","TEXT"),("pan","TEXT"),("created_at","TEXT")]:
        if col not in existing:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")
    c.execute("SELECT COUNT(*) FROM bankers")
    banker_count = c.fetchone()[0]
    c.execute('''INSERT INTO users (name,age,phone,loanAmount,loanType,tenure,emi,risk_score,allocated_banker,loan_status,reason,address,employment,purpose,aadhar,pan,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (data.get('name'), data.get('age',0), data.get('phone'),
         data.get('loanAmount'), data.get('loanType'), data.get('tenure'),
         data.get('emi'), data.get('risk_score'), None, "Pending", "",
         data.get('address',''), data.get('employment',''), data.get('purpose',''),
         data.get('aadhar',''), data.get('pan',''), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return jsonify({"message": "no_banker" if banker_count == 0 else "submitted"})

# PICKUP / BANKER ACTION
@app.route('/pickup_loan', methods=['POST'])
def pickup_loan():
    data = request.json
    user_id = data.get('user_id')
    banker_name = data.get('banker_name','').strip()
    if not user_id or not banker_name:
        return jsonify({"error":"Missing data."}), 400
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT allocated_banker FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error":"Application not found."}), 404
    if row[0]:
        conn.close()
        return jsonify({"error":"Already picked up by another banker."}), 400
    c.execute("UPDATE users SET allocated_banker=?, loan_status=? WHERE id=?", (banker_name,"Picked Up",user_id))
    conn.commit(); conn.close()
    return jsonify({"message":"Picked up successfully."})

@app.route('/banker_action', methods=['POST'])
def banker_action():
    data = request.json
    user_id = data.get('user_id')
    action = data.get('action')
    reason = data.get('reason','')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT loan_status, allocated_banker FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"error":"User not found"}), 404
    current_status, banker = row[0], row[1]
    c.execute("UPDATE users SET loan_status=?, reason=? WHERE id=?", (action,reason,user_id))
    if banker:
        first_action = current_status in ("Pending","Picked Up")
        if current_status=="Approved" and action!="Approved":
            c.execute("UPDATE bankers SET approval=MAX(0,approval-1) WHERE name=?", (banker,))
        elif current_status=="Rejected" and action!="Rejected":
            c.execute("UPDATE bankers SET rejection=MAX(0,rejection-1) WHERE name=?", (banker,))
        elif current_status=="Manual Review" and action!="Manual Review":
            c.execute("UPDATE bankers SET manual=MAX(0,manual-1) WHERE name=?", (banker,))
        if action=="Approved":
            c.execute("UPDATE bankers SET approval=approval+1 WHERE name=?", (banker,))
        elif action=="Rejected":
            c.execute("UPDATE bankers SET rejection=rejection+1 WHERE name=?", (banker,))
        elif action=="Manual Review":
            c.execute("UPDATE bankers SET manual=manual+1 WHERE name=?", (banker,))
        if first_action:
            c.execute("UPDATE bankers SET total_customers=total_customers+1 WHERE name=?", (banker,))
    conn.commit(); conn.close()
    return jsonify({"message":"Action recorded"})

# GET STATUS
@app.route('/get_status/<phone>')
def get_status(phone):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    name = request.args.get('name','').strip()
    if name:
        c.execute('SELECT loan_status,reason,allocated_banker FROM users WHERE phone=? AND name=? ORDER BY id DESC LIMIT 1', (phone,name))
    else:
        c.execute('SELECT loan_status,reason,allocated_banker FROM users WHERE phone=? ORDER BY id DESC LIMIT 1', (phone,))
    data = c.fetchone()
    conn.close()
    if data:
        return jsonify({"status":data[0],"reason":data[1],"banker":data[2] or ""})
    return jsonify({"status":"No Application","reason":"","banker":""})

# USERS / BANKERS / STATS
@app.route('/api/users')
def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"age":r[2],"phone":r[3],"loanAmount":r[4],"loanType":r[5],"tenure":r[6],"emi":r[7],"score":r[8],"banker":r[9],"status":r[10],"reason":r[11]} for r in rows])

@app.route('/users')
def api_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return jsonify([[r[0],r[1],r[3],r[4] or 0,r[5] or "",r[6] or 0,r[7] or 0,r[8] or 0,r[9] or "",r[10] or "Pending",r[11] or ""] for r in rows])

@app.route('/api/bankers')
def get_bankers():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bankers)")
    cols = [col[1] for col in c.fetchall()]
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":dict(zip(cols,b)).get("id",""),"name":dict(zip(cols,b)).get("name",""),"bankName":dict(zip(cols,b)).get("bank_name",""),"branch":dict(zip(cols,b)).get("branch",""),"ifsc":dict(zip(cols,b)).get("ifsc",""),"bankerId":dict(zip(cols,b)).get("banker_id",""),"totalCustomers":dict(zip(cols,b)).get("total_customers",0),"approval":dict(zip(cols,b)).get("approval",0),"rejection":dict(zip(cols,b)).get("rejection",0),"manual":dict(zip(cols,b)).get("manual",0)} for b in rows])

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
        row = dict(zip(cols,r))
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
        r = dict(zip(cols,row))
        return jsonify({"name":r.get("name",""),"bankName":r.get("bank_name",""),"ifsc":r.get("ifsc",""),"branch":r.get("branch",""),"bankerId":r.get("banker_id","")})
    return jsonify({"error":"Not found"}), 404

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users"); total_loans = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE loan_status='Approved'"); approved = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE loan_status='Rejected'"); rejected = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE loan_status='Pending' OR loan_status='Picked Up'"); pending = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM bankers"); total_bankers = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM user_accounts"); total_users = c.fetchone()[0]
    conn.close()
    return jsonify({"total_loans":total_loans,"approved":approved,"rejected":rejected,"pending":pending,"total_bankers":total_bankers,"total_users":total_users})

# ADMIN APIs
@app.route('/api/borrowers')
def api_borrowers():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"age":r[2],"phone":r[3],"loanAmount":r[4],"loanType":r[5],"tenure":r[6],"emi":r[7],"risk_score":r[8],"allocated_banker":r[9],"loan_status":r[10],"reason":r[11]} for r in rows])

@app.route('/api/admin_bankers')
def api_admin_bankers():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bankers)")
    cols = [col[1] for col in c.fetchall()]
    c.execute("SELECT * FROM bankers")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":dict(zip(cols,b)).get("id",""),"name":dict(zip(cols,b)).get("name",""),"bank_name":dict(zip(cols,b)).get("bank_name",""),"branch":dict(zip(cols,b)).get("branch",""),"ifsc":dict(zip(cols,b)).get("ifsc",""),"banker_id":dict(zip(cols,b)).get("banker_id",""),"total_customers":dict(zip(cols,b)).get("total_customers",0),"approval":dict(zip(cols,b)).get("approval",0),"rejection":dict(zip(cols,b)).get("rejection",0),"manual":dict(zip(cols,b)).get("manual",0)} for b in rows])

@app.route('/api/user_accounts')
def get_user_accounts():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_accounts")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"phone":r[2],"username":r[3]} for r in rows])

@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit(); conn.close()
    return jsonify({"message":"Deleted"})

@app.route('/reset_all', methods=['POST'])
def reset_all():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users"); c.execute("DELETE FROM bankers")
    conn.commit(); conn.close()
    return jsonify({"message":"Reset successful"})

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET loan_status=?, reason=? WHERE id=?", (data['status'],data['reason'],data['id']))
    conn.commit(); conn.close()
    return jsonify({"message":"Updated"})

@app.route('/save', methods=['POST'])
def save_data():
    data = request.json
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name,phone,loan_status,reason) VALUES (?,?,?,?)", (data.get('name'),data.get('phone'),"Pending",""))
    conn.commit(); conn.close()
    return jsonify({"message":"Saved"})

@app.route('/admin_remove_banker/<int:id>', methods=['DELETE'])
def admin_remove_banker(id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name FROM bankers WHERE id=?", (id,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE users SET allocated_banker=NULL, loan_status='Pending' WHERE allocated_banker=? AND loan_status NOT IN ('Approved','Rejected')", (row[0],))
    c.execute("DELETE FROM bankers WHERE id=?", (id,))
    conn.commit(); conn.close()
    return jsonify({"message":"Banker removed"})

# BORROWER PROFILE
@app.route('/save_borrower_profile', methods=['POST'])
def save_borrower_profile():
    data = request.json
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(borrower_profiles)")
    existing_cols = [r[1] for r in cur.fetchall()]
    for col in ['aadhar_img','pan_img','salary_img','bank_stmt']:
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE borrower_profiles ADD COLUMN {col} TEXT")
    cur.execute("SELECT id FROM borrower_profiles WHERE phone=?", (data.get('phone',''),))
    row = cur.fetchone()
    fields = (data.get('name',''), data.get('age',0), data.get('email',''),
              data.get('address',''), data.get('employment',''), data.get('employer',''),
              data.get('aadhar',''), data.get('pan',''), data.get('purpose',''),
              data.get('accountHolder',''), data.get('accountNumber',''), data.get('ifsc',''),
              data.get('aadharImg'), data.get('panImg'), data.get('salaryImg'), data.get('bankStmt'))
    if row:
        cur.execute('''UPDATE borrower_profiles SET name=?,age=?,email=?,address=?,employment=?,employer=?,aadhar=?,pan=?,purpose=?,account_holder=?,account_number=?,ifsc=?,aadhar_img=?,pan_img=?,salary_img=?,bank_stmt=? WHERE phone=?''', fields + (data.get('phone',''),))
    else:
        cur.execute('''INSERT INTO borrower_profiles (name,phone,age,email,address,employment,employer,aadhar,pan,purpose,account_holder,account_number,ifsc,aadhar_img,pan_img,salary_img,bank_stmt,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (data.get('name',''), data.get('phone','')) + fields[1:] + (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
    conn.commit(); conn.close()
    return jsonify({"message": "saved"})

@app.route('/api/borrower_profile')
def get_borrower_profile():
    phone = request.args.get('phone','').strip()
    name = request.args.get('name','').strip()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    if phone and name:
        c.execute("SELECT * FROM borrower_profiles WHERE phone=? OR name=? LIMIT 1",(phone,name))
    elif phone:
        c.execute("SELECT * FROM borrower_profiles WHERE phone=? LIMIT 1",(phone,))
    else:
        c.execute("SELECT * FROM borrower_profiles WHERE name=? LIMIT 1",(name,))
    row = c.fetchone()
    c2 = conn.cursor()
    c2.execute("PRAGMA table_info(borrower_profiles)")
    cols = [r[1] for r in c2.fetchall()]
    conn.close()
    if row:
        return jsonify(dict(zip(cols, row)))
    return jsonify({"error":"not found"}), 404

@app.errorhandler(404)
def not_found(e): return render_template('404.html'), 404
@app.errorhandler(500)
def server_error(e): return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=False)
