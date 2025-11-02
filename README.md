# Pawfect Home — Local development README
=====================================

This README collects everything needed to run the project locally on Windows (PowerShell). It explains how to:

- prepare a Python virtual environment and install dependencies
- start a local MySQL server (XAMPP or MySQL Installer)
- create the database and user
- configure the app (.env)
- run tests and start the Flask app

Important behavior
------------------
- The app attempts to connect to a MySQL database using `DATABASE_URL` from a `.env` file.
- If MySQL is unavailable after a few retries the app will automatically fall back to a local SQLite file at `data/dev.db` so you can continue development.

Table of contents
- Prerequisites
- Files added / edited
- Step 0 — Open PowerShell and workspace
- Step 1 — Install or start MySQL
- Step 2 — Create database and user
- Step 3 — Configure `.env`
- Step 4 — Install Python dependencies (venv)
- Step 5 — Start MySQL helper (optional)
- Step 6 — Run tests and start the app
- Troubleshooting & diagnostics
- Next steps

Prerequisites
-------------
- Windows (PowerShell)
- Python 3.8+ installed and on PATH
- One of the following for MySQL:
	- XAMPP (recommended for quick local setup)
	- MySQL Server + Workbench (official installer)

Files added / edited in this workspace
------------------------------------
- `app.py` — Flask app with SQLAlchemy wiring, auto-start/retry logic for MySQL, and SQLite fallback. Also contains the `Pet` model.
- `start_mysql.ps1` — PowerShell helper to attempt to start common MySQL services or open XAMPP control panel.
- `install_deps.ps1` — PowerShell helper to create & activate `.venv` and install packages from `requirements.txt`.
- `requirements.txt` — project Python dependencies.
- `test_db.py` — small script to test DB connectivity and create sample data.
- `sql/setup_database.sql` — SQL to create `pawfect` DB and `pawuser` user.
- Template and static changes: `templates/` and `static/css/styles.css` (UI updates, billing/vaccination templates).

Step 0 — Open PowerShell and workspace
--------------------------------------
1. Open PowerShell. To manage services, run PowerShell as Administrator.
2. Change to the project folder:

```powershell
cd "C:\Users\pawar\OneDrive\sit clg\pet adoption\python_app"
```

Step 1 — Install or start a local MySQL server
----------------------------------------------
Option A — XAMPP (recommended):
1. Install XAMPP from https://www.apachefriends.org and open the XAMPP Control Panel.
2. Start MySQL from the Control Panel (click Start). Use phpMyAdmin to create DB and users if preferred.

Option B — MySQL Server (official):
1. Install MySQL Installer from https://dev.mysql.com.
2. Start the MySQL Windows service (often named `MySQL80`).

Useful PowerShell checks:

```powershell
# Show mysql related services
Get-Service *mysql* | Format-Table Name, Status -AutoSize

# Test port 3306
Test-NetConnection -ComputerName 127.0.0.1 -Port 3306

# Show processes listening on 3306
netstat -ano | Select-String ":3306"
```

If MySQL is not running you can try the helper script (run PowerShell as Admin):

```powershell
.\start_mysql.ps1
```

Step 2 — Create database and user
----------------------------------
Open Workbench or phpMyAdmin and execute the SQL below (replace the password):

```sql
CREATE DATABASE IF NOT EXISTS pawfect
	CHARACTER SET utf8mb4
	COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'pawuser'@'localhost' IDENTIFIED BY 'StrongP@ssw0rd';
GRANT ALL PRIVILEGES ON pawfect.* TO 'pawuser'@'localhost';
FLUSH PRIVILEGES;
```

If you run into authentication plugin errors, run:

```sql
ALTER USER 'pawuser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'StrongP@ssw0rd';
FLUSH PRIVILEGES;
```

Step 3 — Configure application (.env)
-------------------------------------
Create a `.env` file in the project root (do not commit it):

```
# Example .env
DATABASE_URL="mysql+pymysql://pawuser:StrongP@ssw0rd@127.0.0.1/pawfect"
SESSION_SECRET="replace_with_a_secure_random_value"
```

If you use XAMPP root with no password (dev only):

```
DATABASE_URL="mysql+pymysql://root:@127.0.0.1/pawfect"
```

Step 4 — Install Python dependencies (venv)
-------------------------------------------
Run the helper script to create a virtual environment and install dependencies:

```powershell
# If script execution is restricted, run once as Admin:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install_deps.ps1
```

Manual alternative:

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Step 5 — Start MySQL helper (optional)
---------------------------------------
If MySQL is installed but not running, run (Admin):

```powershell
.\start_mysql.ps1
```

The script will attempt to start `MySQL80`, `MySQL`, or `mysql` services and open XAMPP control panel if detected.

Step 6 — Run tests and start the app
------------------------------------
1. With the virtual environment activated, run the DB test script (this will try MySQL first):

```powershell
python test_db.py
```

2. Start the Flask app:

```powershell
python app.py
```

3. Open http://127.0.0.1:3000 in your browser.

Behavior note: the app will retry connecting to MySQL a few times; if unsuccessful it will use `data/dev.db` (SQLite) and continue.

Troubleshooting & diagnostics
----------------------------
- "mysql : The Term 'mysql' is not recognized" → the MySQL CLI is not on PATH. Use the full path to `mysql.exe` or use XAMPP's shell.
	- Example: `& "C:\xampp\mysql\bin\mysql.exe" -u root -p`
- "Unable to connect to 127.0.0.1:3306" → MySQL service not running. Start XAMPP or the Windows service.
- "Access denied for user" → wrong credentials. Recreate or alter the user in Workbench/phpMyAdmin and update `.env`.
- "No module named 'flask_sqlalchemy'" → venv isn't activated or dependencies not installed. Run `install_deps.ps1`.

If you need debugging help, paste the outputs of these commands here:

```powershell
Get-Service *mysql* | Format-Table Name, Status -AutoSize
netstat -ano | Select-String ":3306"
Test-NetConnection -ComputerName 127.0.0.1 -Port 3306
```

Next steps & recommendations
----------------------------
- Use XAMPP for a simple local dev environment; phpMyAdmin makes creating databases easy.
- For production-like workflows, use MySQL Installer + Workbench and set stronger passwords.
- Replace `db.create_all()` with `Flask-Migrate` (Alembic) for real migrations.
- Consider removing any automatic pip-install attempts inside `app.py` and manage dependencies via `install_deps.ps1`.

Want me to continue?
- I can walk you through creating the DB in phpMyAdmin step-by-step, or
- Help you diagnose the exact errors if you paste the outputs of the diagnostics commands above.

Thank you — paste any errors or command outputs and I will continue troubleshooting.
