# MySQL Navigator

A modern, GUI-based MySQL management tool built with **Python**, **Tkinter**, and **ttkbootstrap**.
MySQL Navigator is designed as a clean replacement for legacy batch scripts and command-line workflows, providing a professional, portfolio-ready desktop application similar in spirit to MySQL Workbench.

---

## 🚀 Features

### Connection Management

* Connect to MySQL using host, port, username, and password
* Visual connection status indicator
* Supports local and remote MySQL servers

### Database Management

* List all user databases (system databases hidden)
* Create new databases
* Drop existing databases with confirmation
* Select active database via TreeView

### Table Management

* View tables inside each database
* Create tables using a visual column builder
* View table data in a grid layout
* Insert, update, and delete records
* Truncate tables
* Delete all records (without resetting auto-increment)

### User Management

* Create MySQL users with different privilege levels:

  * Root user (full access + grant option)
  * Admin user (full access, no grants)
  * Database-specific user
* List all MySQL users with authentication details

### Backup & Export

* Backup selected database using `mysqldump`
* Timestamped `.sql` backups
* Automatic `backups/` directory creation

### SQL Query Tool

* Run custom SQL queries
* View query results in a separate window

### UI & UX

* Modern dark/light themes (toggleable)
* Responsive window sizing
* Scrollable panels for large content
* TreeView-based database and table navigation

---

## 📂 Project Structure

```text
mysql_navigator/
│
├── app.py              # Main GUI application
├── db.py               # MySQL connection & database-level operations
├── operations.py       # Table, record, user & query operations
├── backup.py           # Database backup/export logic
├── config.py           # Shared application state
└── legacy/
    └── Mysql Navigator.bat   # Old batch script (deprecated)
```

---

## 🧠 Architecture Overview

### Shared State (`config.py`)

The application replaces batch variables with a shared Python state:

```python
current_connection = None
current_cursor = None
current_db = None
```

This allows all modules to access the active connection, cursor, and selected database without global hacks or duplicated logic.

---

## 🔧 Core Modules

### `app.py` (GUI Layer)

* Built using `ttkbootstrap` for modern styling
* Handles:

  * Window layout
  * User interactions
  * Dialogs and confirmations
  * TreeView navigation
* Calls logic from `db.py`, `operations.py`, and `backup.py`

### `db.py` (Database Engine)

* Handles MySQL connections
* Lists databases
* Selects active database
* Creates and drops databases

### `operations.py` (Data & User Operations)

* Table creation and management
* CRUD operations (Create, Read, Update, Delete)
* Custom SQL execution
* MySQL user creation and listing

### `backup.py` (Backup Engine)

* Uses `mysqldump` via `subprocess`
* Creates timestamped backups
* Stores backups locally

---

## 🛠️ Requirements

* Python 3.9+
* MySQL Server 5.7 / 8.0+
* `mysqldump` available in PATH

### Python Dependencies

Install required packages:

```bash
pip install mysql-connector-python ttkbootstrap
```

---

## ▶️ Running the Application

1. Clone or download the project
2. Ensure MySQL server is running
3. Install dependencies
4. Run:

```bash
python app.py
```

---

## 🔐 Security Notes

* Passwords are never stored on disk
* MySQL credentials are kept in memory only
* User creation actions require sufficient MySQL privileges

⚠️ Granting ROOT or ADMIN users should be done carefully.

---

## 📦 Backup Output Example

```text
backups/
└── mydatabase_20251215_142233.sql
```

---

## 🧪 Tested On

* Linux (Kali, Ubuntu)
* Windows 10 / 11
* MySQL 8.x

---

## 🎯 Project Goals

* Replace my previous legacy batch scripts
* Demonstrate clean Python architecture
* Showcase GUI + database integration
* Serve as a portfolio-grade desktop application

---

## 🛣️ Future Improvements

* SQL editor with syntax highlighting
* Table designer (ALTER TABLE)
* Data export to CSV / Excel
* Role & privilege editor
* Connection profiles

---

## 👨‍💻 Author

**Daniel Chege**
MySQL Navigator – A modern evolution of classic database tooling

---

## 📜 License

This project is provided for learning and portfolio use.
You are free to modify and extend it as needed.

---

🔥 *My batch script didn’t die — it evolved.*
