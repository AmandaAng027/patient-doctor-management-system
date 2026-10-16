# Installation and Setup Guide

This guide explains how to install and run the Patient Data Management System (PDMS) on Windows.

## Prerequisites

- Windows
- Python 3.10 or later
- Microsoft SQL Server Express
- SQL Server Management Studio (SSMS)
- Microsoft ODBC Driver 17 for SQL Server
- PyCharm Community Edition (recommended) or Command Prompt

## Step 1 — Install Python

1. Download Python 3.10 or later from the [official Python website](https://www.python.org/downloads/).
2. Run the installer.
3. If offered, select **Add Python to PATH**.
4. Finish the installation.

To check that Python is installed, open Command Prompt or PowerShell and run:

```powershell
python --version
```

## Step 2 — Install the Required Python Packages

Open Command Prompt or PowerShell and run:

```powershell
python -m pip install pyodbc tkcalendar fpdf Pillow Werkzeug
```

These packages provide database connectivity, calendar widgets, PDF generation, image handling, and password hashing.

If the project includes a `requirements.txt` file, you can instead install its listed dependencies with:

```powershell
python -m pip install -r requirements.txt
```

## Step 3 — Install SQL Server Express and SSMS

1. Download [SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads).
2. Install SQL Server Express. The **Basic** installation is suitable for a standard local setup.
3. Note the SQL Server instance name shown or configured during installation. A common example is `localhost\SQLEXPRESS`.
4. Download [SQL Server Management Studio (SSMS)](https://learn.microsoft.com/en-us/ssms/install/install).
5. Install SSMS using the installer instructions.

## Step 4 — Install the Microsoft ODBC Driver 17 for SQL Server

1. Open Microsoft's [ODBC Driver download page](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17).
2. Download and install **Microsoft ODBC Driver 17 for SQL Server** for your Windows system.
3. Complete the installation before running the application.

The driver name in the application's database connection configuration must match the installed driver.

## Step 5 — Set Up the PDMS Database

**Important:** Run only a reviewed, portable version of the project's SQL setup script. The original development script may contain machine-specific database file paths and sample account data, so do not run that original script on another computer until it has been cleaned and verified.

Once a cleaned setup script is available:

1. Open SSMS.
2. In the **Connect to Server** window, enter your SQL Server instance name (for example, `localhost\SQLEXPRESS`) and connect.
3. Open the cleaned PDMS setup script in SSMS using **File → Open → File**.
4. Review the script, then click **Execute** or press **F5**.
5. In Object Explorer, expand **Databases → PDMS → Tables** and confirm that the database and tables were created.

If a cleaned setup script has not yet been included in the repository, do not assume the database will be created automatically. The database schema must be created before the application can connect successfully.

## Step 6 — Configure the Database Connection

The project uses Windows Authentication to connect to SQL Server.

The updated `data_access_layer.py` reads the SQL Server instance name from the `PDMS_SERVER` environment variable. If it is not set, it uses `localhost\SQLEXPRESS` as the default.

### Option A — Use the default instance name

If your SQL Server instance is named `localhost\SQLEXPRESS`, no additional configuration is needed.

### Option B — Set your own SQL Server instance name

If your instance has a different name, open PowerShell and run the following command, replacing the example with your actual server/instance name:

```powershell
$env:PDMS_SERVER = "YOUR_COMPUTER_NAME\SQLEXPRESS"
```

For example, if your SQL Server instance is named `AmandaNitro\SQLEXPRESS`:

```powershell
$env:PDMS_SERVER = "AmandaNitro\SQLEXPRESS"
```

Keep the same PowerShell window open when you start the application, because this environment variable applies to that session.

To find the correct instance name, check the **Server name** field in SSMS's **Connect to Server** window.

## Step 7 — Run the Application

### Option A — Using PyCharm Community Edition (recommended)

1. Open PyCharm.
2. Select **File → Open** and choose the PDMS project folder.
3. In the project panel, locate `main.py`.
4. Right-click `main.py` and select **Run 'main'**.
5. The login window should appear if the database connection and setup are correct.

If you set `PDMS_SERVER` in PowerShell, make sure PyCharm has that environment variable configured in the run configuration, or launch the application from the same PowerShell session instead.

### Option B — Using PowerShell or Command Prompt

1. Open PowerShell or Command Prompt.
2. Change to the project directory. Replace the example path with the folder where you saved the project:

   ```powershell
   cd "C:\path\to\PDMS_Project"
   ```

3. If needed, set the SQL Server instance name in PowerShell:

   ```powershell
   $env:PDMS_SERVER = "YOUR_COMPUTER_NAME\SQLEXPRESS"
   ```

4. Run the application:

   ```powershell
   python main.py
   ```

5. The login window should appear if setup is complete.

## Troubleshooting

- **`No module named ...`** — Install the missing package using `python -m pip install package-name`.
- **ODBC driver not found** — Confirm that Microsoft ODBC Driver 17 for SQL Server is installed and the driver name matches the connection configuration.
- **Cannot connect to SQL Server** — Confirm that SQL Server is installed and running, and that `PDMS_SERVER` matches the instance name shown in SSMS.
- **Database `PDMS` does not exist** — Complete the database setup using the cleaned SQL setup script.
- **Login fails for an old sample account** — The updated application verifies hashed passwords. Plaintext sample passwords from an older database are not compatible with the new password-verification logic. Register a new account or use a database setup prepared for the updated application.

## Notes

- The application requires a configured SQL Server database; installing Python packages alone is not sufficient.
- Use fictional test data when demonstrating the project.
- Do not publish real patient information, passwords, database backups, or other confidential data in a public repository.
