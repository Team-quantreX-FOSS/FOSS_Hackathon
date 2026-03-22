// ================= REGISTER =================
function registerUser() {
    let name = document.getElementById("name")?.value;
    let phone = document.getElementById("phone")?.value;
    let username = document.getElementById("username")?.value;
    let password = document.getElementById("password")?.value;
    let confirmPassword = document.getElementById("confirmPassword")?.value;

    if (!name || !phone || !username || !password || !confirmPassword) {
        alert("Please fill all fields");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    let user = {
        name,
        phone,
        username,
        password,
        riskScore: 0,
        riskLevel: "New"
    };

    localStorage.setItem(username, JSON.stringify(user));

    alert("Registered Successfully!");
    window.location.href = "login.html";
}

// ================= LOGIN =================
function loginUser() {
    let username = document.getElementById("loginUsername")?.value;
    let password = document.getElementById("loginPassword")?.value;

    let storedUser = JSON.parse(localStorage.getItem(username));

    if (!storedUser || storedUser.password !== password) {
        alert("Username and Password not matched!");
        return;
    }

    localStorage.setItem("currentUser", username);

    // ✅ FIXED REDIRECT
    window.location.href = "dashboard.html";
}

// ================= DASHBOARD LOAD =================
function loadDashboard() {
    let currentUser = localStorage.getItem("currentUser");

    if (!currentUser) return;

    let user = JSON.parse(localStorage.getItem(currentUser));

    let scoreEl = document.getElementById("riskScore");
    let levelEl = document.getElementById("riskLevel");

    if (scoreEl) scoreEl.innerText = user?.riskScore || 0;
    if (levelEl) levelEl.innerText = user?.riskLevel || "New";

    loadCharts();
}

// ================= NAVIGATION =================
function goToLoan() {
    window.location.href = "loan.html";
}

// ================= LOAN CALC =================
function calculateLoan() {
    let income = parseInt(document.getElementById("income")?.value) || 0;
    let expense = parseInt(document.getElementById("expense")?.value) || 0;
    let emi = parseInt(document.getElementById("existingEmi")?.value) || 0;

    let food = parseInt(document.getElementById("food")?.value) || 0;
    let rent = parseInt(document.getElementById("rent")?.value) || 0;
    let travel = parseInt(document.getElementById("travel")?.value) || 0;
    let others = parseInt(document.getElementById("others")?.value) || 0;

    let disposable = income - expense - emi;

    let score = 0;
    if (disposable > 50000) score = 80;
    else if (disposable > 20000) score = 60;
    else score = 40;

    let riskLevel = "";
    let color = "";

    if (score >= 75) {
        riskLevel = "Low Risk";
        color = "green";
    } else if (score >= 50) {
        riskLevel = "Medium Risk";
        color = "orange";
    } else {
        riskLevel = "High Risk";
        color = "red";
    }

    let loanAmount = Math.max(disposable * 10, 0);
    let emiEstimate = Math.max(Math.round(loanAmount / 12), 0);

    let resultEl = document.getElementById("result");

    if (resultEl) {
        resultEl.innerHTML = `
            <p>Risk Score: ${score}</p>
            <p style="color:${color}">Risk Level: ${riskLevel}</p>
            <p>Recommended Loan: ₹${loanAmount}</p>
            <p>Estimated EMI: ₹${emiEstimate}</p>
        `;
    }

    // SAVE USER DATA
    let currentUser = localStorage.getItem("currentUser");
    let user = JSON.parse(localStorage.getItem(currentUser));

    if (user) {
        user.riskScore = score;
        user.riskLevel = riskLevel;
        localStorage.setItem(currentUser, JSON.stringify(user));
    }

    // SAVE FOR CHARTS
    localStorage.setItem("income", income);
    localStorage.setItem("expense", expense);
    localStorage.setItem("food", food);
    localStorage.setItem("rent", rent);
    localStorage.setItem("travel", travel);
    localStorage.setItem("others", others);
}

// ================= CHARTS =================
function loadCharts() {
    if (typeof Chart === "undefined") return;

    let income = parseInt(localStorage.getItem("income")) || 0;
    let expense = parseInt(localStorage.getItem("expense")) || 0;

    let food = parseInt(localStorage.getItem("food")) || 0;
    let rent = parseInt(localStorage.getItem("rent")) || 0;
    let travel = parseInt(localStorage.getItem("travel")) || 0;
    let others = parseInt(localStorage.getItem("others")) || 0;

    let barCanvas = document.getElementById("barChart");
    let pieCanvas = document.getElementById("pieChart");

    if (barCanvas) {
        new Chart(barCanvas, {
            type: "bar",
            data: {
                labels: ["Income", "Expense"],
                datasets: [{
                    data: [income, expense],
                    backgroundColor: ["#8ad18d5d", "#f4433634"]
                }]
            }
        });
    }

    if (pieCanvas) {
        new Chart(pieCanvas, {
            type: "pie",
            data: {
                labels: ["Food", "Rent", "Travel", "Others"],
                datasets: [{
                    data: [food, rent, travel, others],
                    backgroundColor: ["#2196F3", "#FF9800", "#4CAF50", "#9C27B0"]
                }]
            }
        });
    }
}

