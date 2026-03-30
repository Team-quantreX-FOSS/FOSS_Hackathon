

# **FinRisk – Detailed System Architecture (User & Action Flow)**

### **1. Overview**

FinRisk is a **multi-user fintech platform** with three roles: **Borrower, Banker, Admin**. Every action is **processed via backend (Flask + SQLite)**, ensuring **multi-device sync** and **real-time updates**.

We’ll describe **each component, button, and what happens on click**.

---

## **2. Borrower Flow**


[Landing Page]
  ├── Register Button
  │    └── Opens Registration Form (Name, Email, Phone, Password)
  │         → On Submit: Backend validates → creates user → redirect to Login
  ├── Login Button
       └── Opens Login Form
            → On Submit: Backend validates → creates session → redirect to Borrower Dashboard


### **Borrower Dashboard Components**

[Dashboard]
  ├── Financial Input Section
  │    ├── Income Field
  │    ├── Expenses Field
  │    ├── EMIs Field
  │    └── Submit Button
  │         → Backend stores data → recalculates Net Savings → updates charts
  ├── Loan Eligibility Checker
  │    ├── Check Eligibility Button
  │         → Backend fetches borrower data + alternative data
  │         → Calculates Risk Score (RBI/CIBIL + Alternative)
  │         → Returns Risk Status (Low / Medium / High)
  │         → Frontend displays score + advice
  ├── Apply Loan
  │    ├── Loan Type Dropdown
  │    ├── Tenure Field
  │    ├── Age Field
  │    └── Submit Button
  │         → Sends loan request to backend → marks as "Pending" → available for Banker
  ├── Real-Time Status
  │    └── Notifications Panel
  │         → Backend sends updates on approval/rejection/pickup
  ├── Loan History & Spending Tracker
  │    ├── Expense Upload Button (Receipts / Bills)
  │    │     → Saves files in backend → updates charts
  │    └── Category Breakdown Charts
  │          → Fetches data → shows charts via Chart.js
  ├── Financial Advisory
  │    └── View Advice Button
  │          → Backend calculates recommendations based on savings rate & risk score
  ├── Government Schemes
  │    └── View Schemes Button
  │          → Opens list with working links (APY, PMJDY, etc.)
  └── Future Planning & Courses
       ├── Set Goal Button
       │     → Backend stores goal → calculates monthly savings required
       └── View Courses Button
             → Fetch curated course list → shows links (NPTEL, Google, SEBI, AWS, CFA)



## **3. Banker Flow**

[Login Page]
  └── Login Form
       → Backend validates → creates session → redirect to Banker Dashboard

### **Banker Dashboard Components**

[Dashboard]
  ├── Unassigned Loan Requests
  │    ├── List of Pending Requests
  │    ├── Pick Request Button
  │          → Marks loan as assigned → borrower notified via notification panel
  ├── Approve / Reject / Manual Review Buttons
  │    ├── Approve
  │    │     → Updates backend → sets status "Approved" → borrower notified
  │    ├── Reject
  │    │     → Updates backend → sets status "Rejected" → borrower notified
  │    └── Manual Review
  │          → Opens popup → banker adds reason → backend updates → borrower notified
  ├── Freeze Buttons
  │    └── Prevent duplicate actions (backend locks loan record)
  └── Performance Stats
       ├── Approval %
       ├── Rejection %
       └── Total Cases Processed
            → Fetches backend data → displays charts


## **4. Admin Flow**:

[Admin Login Page]
  └── Login Form
       → Backend validates → creates session → redirect to Admin Dashboard


### **Admin Dashboard Components**

[Dashboard]
  ├── Bank Management
  │    ├── View Banks Table (Branch, IFSC, Banker Count)
  │    └── Performance Charts
  │          → Pull data → Pie charts / Bar charts via Chart.js
  ├── Borrower Management
  │    ├── View Borrowers Table
  │    └── Loan Applications Table
  │          → Filter / Search / Sort → Backend queries
  ├── Banker Management
  │    ├── View Banker Table
  │    └── Individual + Overall Charts
  └── Live System Stats
       ├── Active Borrowers
       ├── Pending Loans
       └── Total Approvals / Rejections
            → Backend API → Updates in real-time


## **5. Backend Workflow**:

[Backend (Flask + SQLite)]
  ├── Handles Authentication
  │    ├── Sessions
  │    └── Multi-device Login (same data across devices)
  ├── Handles Data Storage
  │    ├── Users (Borrowers, Bankers, Admins)
  │    ├── Loans
  │    ├── Expenses
  │    └── Notifications
  ├── Risk Scoring Engine
  │    ├── Standard Factors (FOIR, Credit Score, Savings Rate, LTI, Age)
  │    └── Alternative Data (Digital footprint, transaction patterns)
  │          → Outputs risk score → stored + sent to front-end
  ├── Notification Engine
  │    └── Sends live status updates to borrowers (loan assigned, approved, rejected)
  └── Charts & Analytics API
       └── Provides JSON data → Frontend Chart.js visualization
       

## **6. Data Flow Diagram (High Detail)**:

'
          ┌───────────────┐
          │   Borrower    │
          │  Actions:     │
          │  - Input Data │
          │  - Apply Loan │
          │  - Track     │
          └─────┬─────────┘
                │ POST / GET
                ▼
        ┌───────────────┐
        │   Backend     │
        │ - Auth        │
        │ - Risk Engine │
        │ - DB Storage  │
        │ - Notifications
        │ - Analytics   │
        └─────┬─────────┘
   Fetch / Update │ Multi-device Sync
                ▼
          ┌───────────────┐
          │  Banker/Admin │
          │ Actions:      │
          │ - Approve     │
          │ - Reject      │
          │ - View Stats  │
          └───────────────┘

