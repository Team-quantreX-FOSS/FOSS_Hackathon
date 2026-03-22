# FOSS_Hackathon
🏦 FinRisk — AI-Powered Borrower Risk Analyzer

A full-stack fintech web application for intelligent loan risk assessment, built for the FOSS Hackathon.


📌 What is FinRisk?
FinRisk is a real-time loan risk analysis platform that connects borrowers, bankers, and admins in a seamless digital loan workflow — powered by RBI/CIBIL-standard risk scoring, government scheme discovery, future financial planning, and skill development resources.

🚀 Features:-
👤 Borrower

Register and login securely
Enter financial details (income, expenses, EMIs)
Loan Eligibility Checker — 5-factor RBI/CIBIL scoring model (FOIR, Credit Score, Savings Rate, LTI, Age)
Apply for Loan — submit application with age, loan type, tenure
Real-time Status Tracking — live notifications when banker picks up, approves, or rejects
Loan History & Spending Tracker — log expenses with bill upload, view category breakdown charts
Financial Advisory — personalised advice based on savings rate and risk score
Government Schemes — 12 official schemes with working links (APY, PMJDY, PMJJBY, MUDRA, etc.)
Future Planning — set short/mid/long-term goals, see monthly savings needed
Skill & Courses — 15 curated free and paid courses (NPTEL, Google, SEBI, AWS, CFA)

🏦 Banker

Register with bank name, branch, IFSC, and banker ID
View unassigned loan requests and pick them up
Approve / Reject / Manual Review with reason
Approve and Reject buttons freeze after action (prevents accidental changes)
Manual Review opens a decision popup
Performance stats (approval %, rejection %, total cases)

⚙ Admin

View all registered banks with branch, IFSC, banker count, and performance
View all borrowers and loan applications
View all bankers with individual and overall pie charts
Live system stats on landing page


🧠 Risk Scoring Model

Based on RBI circulars, CIBIL methodology and NBFC lending norms:
Factor:- CIBIL Score, FOIR (Fixed Obligation to Income Ratio), Net Savings Rate, LTI (Loan to Annual Income), Age Factor
Weight: 35pts, 25 pts, 20 pts, 12 pts, 8 pts
Standard: TransUnion CIBIL, RBI circular, Income − Expenses, RBI/NHB guideline, PSB lending norms
Hard knockouts: CIBIL < 550 → capped at 30 pts. FOIR > 65% → capped at 25 pts.

🛠 Tech Stack
Layer:- Backend, Database, Frontend, Charts, Fonts, Auth
Technology: Python 3.11 and Flask, SQLite3, HTML5 and  CSS3 and Vanilla and JavaScript, Chart.js, Syne and DM Mono (Google Fonts), localStorage (client-side)
