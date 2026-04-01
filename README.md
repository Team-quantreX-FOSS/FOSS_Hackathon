# FOSS_Hackathon 2026

🏦 **FinRisk — AI-Powered Borrower Risk Analyzer (Multi-Device, Backend-Driven)**

A full-stack fintech web application for **intelligent loan risk assessment**, designed for **FOSS Hackathon 2026** with a focus on open-source contribution, real-world impact, and robust architecture.

**Demo Video** →(https://drive.google.com/file/d/1LeaCKgHhyqiAyc152S5b2mXJlygtIdB0/view?usp=sharing)

---

## 📌 About FinRisk

FinRisk is a real-time, backend-driven loan risk analysis platform that connects borrowers, bankers, and admins in a seamless digital loan workflow. It integrates RBI/CIBIL-standard scoring, alternative data risk assessment, government scheme discovery, and future financial planning.

With **backend-based data storage**, users can login from multiple devices and see consistent, real-time financial and loan data.

---

## 🚀 Key Features

### 👤 Borrower
- Secure Registration & Login – Multi-device, session-based authentication.
- Financial Input Dashboard – Income, expenses; data stored securely in backend.
- Loan Eligibility Checker – Enhanced 5-factor scoring model (FOIR, Credit Score, Savings Rate, LTI, Age).
- Apply for Loan – Submit requests with tenure, type, and age.
- Real-Time Status Updates – Notifications when banker picks, approves, or rejects.
- Loan & Expense Tracker – Upload bills, categorize expenses, view breakdown charts.
- Financial Advisory – Recommendations based on risk score and savings trends.
- Government Schemes – Access official schemes (APY, PMJDY, PMJJBY, MUDRA) with working links.
- Future Planning & Skill Development – Set goals and access curated courses.

### 🏦 Banker
- Banker Registration – Branch, IFSC, Banker ID.
- Loan Request Dashboard – Pick unassigned requests.
- Decision Workflow – Approve / Reject / Manual Review (with reasons).
- Freeze Action Buttons – Prevent accidental duplicate decisions.
- Performance Analytics – Approval %, rejection %, total processed.

### ⚙ Admin
- Overview Dashboard – All banks, borrowers, and bankers.
- Detailed Analytics – Individual and overall charts.
- Live System Stats – Active borrowers, pending loans, approvals.

---

## 🧠 Risk Scoring Model

**Hybrid scoring using standard and alternative data sources**:

| Factor                        | Weight | Source                              |
|-------------------------------|--------|-------------------------------------|
| CIBIL / Credit Score          | 35 pts | TransUnion CIBIL                    |
| FOIR                          | 25 pts | RBI Circulars / NBFC norms          |
| Net Savings Rate              | 20 pts | Income - Expenses (User Input)      |
| LTI (Loan to Annual Income)   | 12 pts | Calculated from financial data      |
| Age Factor                    | 8 pts  | RBI/NHB Lending Norms               |

**Hard Knockouts:**
- CIBIL < 550 → capped at 30 pts
- FOIR > 65% → capped at 25 pts

**Alternative Data Risk Integration:** Uses digital footprint, utility payments, and micro-transactions to support underbanked users.

---

## 🛠 Tech Stack & Architecture

- **Backend:** Python 3.11, Flask
- **Database:** SQLite3 (multi-device support)
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js
- **Fonts:** Google Fonts (Syne, DM Mono)
- **Authentication:** Session-based

All interactions pass through the backend for secure, synchronized data across devices.

---

## 💻 Installation & Usage

**Prerequisites:** Python 3.8 or higher

**Steps:**

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/FinRisk.git
cd FinRisk

# 2. Create virtual environment
python -m venv venv

# Activate the virtual environment:

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py

⚠️ Note: A minor session configuration issue was fixed post-submission for deployment stability.
