

# FOSS_Hackathon 2026

🏦 **FinRisk — AI-Powered Borrower Risk Analyzer (Multi-Device, Backend-Driven)**

A full-stack fintech web application for **intelligent loan risk assessment**, designed for **FOSS Hackathon 2026** with a focus on **open-source contribution, real-world impact, and robust architecture**.

---

## 📌 About FinRisk

FinRisk is a **real-time, AI-powered loan risk analysis platform** that connects borrowers, bankers, and admins in a seamless digital loan workflow. It integrates **RBI/CIBIL-standard scoring, alternative data risk assessment, government scheme discovery, and future financial planning**.

Now with **backend-based data storage**, users can **login from multiple devices** and see consistent, real-time financial and loan data.

---

## 🚀 Key Features

### 👤 Borrower

* **Secure Registration & Login** – Multi-device, session-based authentication.
* **Financial Input Dashboard** – Income, expenses, EMIs; data stored securely in backend.
* **Loan Eligibility Checker** – Enhanced 5-factor scoring model:

  * **Standard Factors:** FOIR, Credit Score, Savings Rate, LTI, Age
  * **Alternative Data:** Social footprint, transaction history patterns, digital footprint → feeds risk score
* **Apply for Loan** – Submit requests with tenure, type, and age.
* **Real-Time Status Updates** – Notifications when banker picks, approves, or rejects.
* **Loan & Expense Tracker** – Upload bills, categorize expenses, view breakdown charts.
* **Financial Advisory** – AI-driven recommendations based on risk score and savings trends.
* **Government Schemes** – Access 12 official schemes (APY, PMJDY, PMJJBY, MUDRA) with working links.
* **Future Planning & Skill Development** – Set goals; 15 curated courses from NPTEL, Google, SEBI, AWS, CFA.

### 🏦 Banker

* **Banker Registration** – Branch, IFSC, Banker ID.
* **Loan Request Dashboard** – Pick unassigned requests.
* **Decision Workflow** – Approve / Reject / Manual Review (with reasons).
* **Freeze Action Buttons** – Prevent accidental duplicate decisions.
* **Performance Analytics** – Approval %, rejection %, total processed.

### ⚙ Admin

* **Overview Dashboard** – All banks, borrowers, and bankers.
* **Detailed Analytics** – Individual and overall charts, performance metrics.
* **Live System Stats** – Landing page shows active borrowers, pending loans, approvals.

---

## 🧠 Risk Scoring Model

**Hybrid scoring using standard and alternative data sources**:

| Factor                                  | Weight | Source                         |
| --------------------------------------- | ------ | ------------------------------ |
| CIBIL / Credit Score                    | 35 pts | TransUnion CIBIL               |
| FOIR (Fixed Obligation to Income Ratio) | 25 pts | RBI Circulars / NBFC norms     |
| Net Savings Rate                        | 20 pts | Income - Expenses (User Input) |
| LTI (Loan to Annual Income)             | 12 pts | Calculated from financial data |
| Age Factor                              | 8 pts  | RBI/NHB Lending Norms          |

**Hard Knockouts:**

* CIBIL < 550 → capped at 30 pts
* FOIR > 65% → capped at 25 pts

**Alternative Data Risk Integration:**

* Uses digital footprint, utility payments, and micro-transactions
* Supplements traditional metrics for borrowers without formal credit history

**Final Risk Score = Weighted Standard Score + Alternative Data Score**

* Enables **more inclusive lending** for underbanked users

---

## 🛠 Tech Stack & Architecture

**Backend:** Python 3.11, Flask

**Database:** SQLite3 (multi-device support)

**Frontend:** HTML5, CSS3, JavaScript, Chart.js

**Fonts:** Google Fonts (Syne, DM Mono)

**Authentication:** Session-based, JWT-compatible for multi-device login

**Data Flow:** Backend stores all user, loan, and analytics data → ensures **consistent multi-device experience**

 💻 **Installation & Usage**

## Prerequisites
- Python 3.8+

### Steps

bash:
# 1. Clone the repository
git clone https://github.com/yourusername/FinRisk.git
cd FinRisk

# 2. Create and activate virtual environment (recommended)
python -m venv venv
# On Windows:
# venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py


**Notes:**

* All interactions pass through backend → ensures **secure, synchronized data**.
* Risk Scoring Engine runs in backend → outputs risk scores visible to borrower, banker, admin.
* Notifications handled via backend → real-time status updates.
* Charts & analytics generated via frontend pulling backend JSON endpoints.
