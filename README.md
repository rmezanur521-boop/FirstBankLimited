# 🏦 First Bank Limited — Desktop Banking System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2.2-green?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791?style=for-the-badge&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**A full-featured, real-world desktop banking application built with Python, CustomTkinter, and PostgreSQL.**

</div>

---

## 📌 Overview

**First Bank Limited** is a complete desktop banking management system designed to simulate real-world banking operations. It features three distinct user roles — Admin, Employee, and Customer — each with their own dedicated panel, permissions, and workflows. The system handles everything from account creation and fund transfers to loan management and KYC document storage.

---

## ✨ Features

### 🔐 Authentication & Roles
- Unified login screen with role selection (Admin / Employee / Customer)
- Customer self-registration from the login screen
- Secure bcrypt password hashing
- Role-based access control across all panels

### 🛠️ Admin Panel
| Feature | Description |
|---|---|
| Dashboard | Live stats — total customers, accounts, balances, today's transactions, loan summary |
| Customer Management | Add, edit, view, delete customers with KYC documents |
| Account Management | Open accounts, deposit, withdraw, freeze/unfreeze |
| Transaction Log | Full transaction history with type, fee, and net amount |
| Loan Management | View, approve, and reject loan applications with reason |
| Employee Management | Create, update, and deactivate employee accounts |
| Settings | Configure bank profile, transfer fee %, and loan interest rate |

### 👔 Employee Panel
- Customer and account management (same as admin, minus sensitive controls)
- Transaction visibility
- Personal dashboard with daily stats

### 👤 Customer Panel
| Feature | Description |
|---|---|
| Dashboard | Account overview, balance, quick actions, last 5 transactions |
| Account Details | Per-account balance, type, and transaction breakdown |
| Fund Transfer | Transfer to own accounts (no fee) or other customers (fee applies) |
| Loan Application | Apply with EMI preview, track status, view outstanding amount |
| Transaction History | Full history with date and amount filters |

### 💰 Transfer Fee System
- **Own account → Own account:** 0% fee (configurable)
- **Own account → Other customer:** Configurable % fee (default 1.5%)
- Live fee preview shown before confirming any transfer
- All fees tracked in transaction records

### 📋 Loan System
- Customer applies → status: **Pending**
- Admin reviews → **Approve** (amount credited instantly) or **Reject** (with reason)
- EMI calculation using standard reducing balance formula
- Full loan lifecycle: Pending → Approved → Active → Closed

---

## 🗂️ Project Structure
FirstBankLimited/
│
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── .env                           # Environment config (not committed)
│
├── config/
│   └── database.py                # PostgreSQL connection pool
│
├── models/                        # Database layer
│   ├── admin.py
│   ├── employee.py
│   ├── customer.py
│   ├── account.py
│   ├── transaction.py
│   └── loan.py
│
├── controllers/                   # Business logic
│   ├── auth_controller.py
│   ├── account_controller.py
│   ├── customer_controller.py
│   └── loan_controller.py
│
├── views/
│   ├── shared/
│   │   ├── login_window.py        # Login + Registration
│   │   └── widgets.py             # Reusable UI components
│   ├── admin/                     # Full admin panel
│   ├── employee/                  # Employee panel
│   └── customer/                  # Customer portal
│
├── utils/
│   ├── helpers.py                 # Formatters & validators
│   ├── image_handler.py           # Photo/document storage
│   └── fee_calculator.py          # Transfer fee logic
│
└── uploads/                       # Stored KYC documents & photos

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 15 or higher
- PyCharm IDE (recommended)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/first-bank-limited.git
cd first-bank-limited
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment**

Create a `.env` file in the root directory:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=first_bank_limited
DB_USER=postgres
DB_PASSWORD=your_password_here
ADMIN_DEFAULT_PASSWORD=Admin@1234
```

**4. Set up the database**

Open pgAdmin or psql and run the full SQL schema from `database/schema.sql`:
```bash
psql -U postgres -f database/schema.sql
```

**5. Create uploads folder**
```bash
mkdir uploads
```

**6. Run the application**
```bash
python main.py
```

---

## 🔑 Default Login Credentials

| Role | Username | Password |
|---|---|---|
| 👑 Admin | `admin` | `Admin@1234` |
| 👔 Employee | *(created by admin)* | *(set by admin)* |
| 👤 Customer | *(self-register)* | *(chosen at registration)* |

> ⚠️ Change the default admin password immediately after first login via Settings.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI Framework | CustomTkinter 5.2.2 |
| Database | PostgreSQL 15+ |
| DB Connector | psycopg2-binary |
| Password Hashing | bcrypt |
| Image Processing | Pillow |
| Config Management | python-dotenv |
| IDE | PyCharm |

---

## 🗄️ Database Schema

The system uses **13 tables** with full relational integrity:
roles → admins, employees, customers
customers → accounts → transactions
accounts → loans → loan_repayments
bank_settings (fees, rates, profile)
audit_logs (full activity trail)

Key database features:
- Auto-generated account numbers (`FBL0000000001`)
- Auto-generated transaction references (`TXN202506010000001`)
- Auto-generated loan references (`LN202506010000001`)
- Trigger-based ID generation
- Views for dashboard stats and account summaries

---

## 📸 Screenshots

> Add your screenshots here after running the application.

| Login Screen | Admin Dashboard |
|---|---|
| ![Login](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) |

| Loan Management | Fund Transfer |
|---|---|
| ![Loans](screenshots/loans.png) | ![Transfer](screenshots/transfer.png) |

---

## 🔒 Security Features

- All passwords hashed with **bcrypt** (never stored as plain text)
- Role-based access — customers cannot access admin/employee routes
- KYC document verification flag per customer
- Account freeze/unfreeze capability
- Audit log table for all critical actions

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 👨‍💻 Author

Built with ❤️ using Python, CustomTkinter, and PostgreSQL.

> *First Bank Limited — Secure • Reliable • Trusted*

