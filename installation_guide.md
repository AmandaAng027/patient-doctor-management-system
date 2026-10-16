# Installation and Setup Guide

This guide explains how to install and run the Patient-Doctor Management System (PDMS) on Windows.

## Step 1 - Install Python

1. Download Python 3.10 or later from the [Python website](https://www.python.org/downloads/).
2. Run the installer and follow the instructions.
3. If the option appears, check **Add Python to PATH** before installing.

To check if Python was installed, open Command Prompt or PowerShell and type:

```powershell
python --version
```

## Step 2 - Install the Required Packages

Open Command Prompt or PowerShell and run:

```powershell
python -m pip install pyodbc tkcalendar fpdf Pillow Werkzeug
```

These packages are used for the database connection, calendar, PDF files, images, and password hashing.

## Step 3 - Install SQL Server Express and SSMS

1. Download [SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads).
2. Install it. The Basic installation should be fine for a local setup.
3. Take note of your SQL Server instance name. It may look like `localhost\SQLEXPRESS`.
4. Download [SQL Server Management Studio (SSMS)](https://learn.microsoft.com/en-us/ssms/install/install).
5. Install SSMS using the default options.

## Step 4 - Install the ODBC Driver

1. Go to the [Microsoft ODBC Driver download page](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17).
2. Download and install **Microsoft ODBC Driver 17 for SQL Server**.

The application uses this driver to connect Python to SQL Server.

## Step 5 - Set Up the PDMS Database

**Note:** The original `script.sql` still needs to be checked and cleaned before it is shared publicly. It contains computer-specific database paths and sample account data. Do not run that original script on another computer until a cleaned version is ready.

When the cleaned setup script is available:

1. Open SSMS.
2. In the Connect to Server window, enter your SQL Server instance name (for example, `localhost\SQLEXPRESS`) and connect.
3. Open the cleaned PDMS setup script using **File -> Open -> File**.
4. Click **Execute** or press **F5**.
5. In Object Explorer, expand **Databases -> PDMS -> Tables** to check that the tables were created.

The database needs to be set up before you run the application.

## Step 6 - Configure the Database Connection

The project uses Windows Authentication to connect to SQL Server.

In `data_access_layer.py`, the application uses the `PDMS_SERVER` environment variable for the SQL Server instance name. If you do not set it, the default is `localhost\SQLEXPRESS`.

If your SQL Server instance has a different name, open PowerShell and enter the following command, replacing the example with your own instance name:

```powershell
$env:PDMS_SERVER = "YOUR_COMPUTER_NAME\SQLEXPRESS"
```

For example:

```powershell
$env:PDMS_SERVER = "AmandaNitro\SQLEXPRESS"
```

Keep that PowerShell window open when running the application. This setting only applies to that PowerShell session.

You can check your instance name in the Server name field in SSMS.

## Step 7 - Run the Application

### Option A - Using PyCharm (recommended)

1. Open PyCharm.
2. Select **File -> Open** and choose the PDMS project folder.
3. Find `main.py` in the project panel.
4. Right-click `main.py` and select **Run 'main'**.
5. The login window should appear if the database is set up correctly.

If you configured `PDMS_SERVER` in PowerShell, you may need to add the same variable to PyCharm's run configuration. Otherwise, you can run the application from that PowerShell window.

### Option B - Using PowerShell or Command Prompt

1. Open PowerShell or Command Prompt.
2. Go to the folder where you saved the project. Replace the example path with your actual folder path:

   ```powershell
   cd "C:\path\to\PDMS_Project"
   ```

3. If needed, set your SQL Server instance name in PowerShell:

   ```powershell
   $env:PDMS_SERVER = "YOUR_COMPUTER_NAME\SQLEXPRESS"
   ```

4. Run the application:

   ```powershell
   python main.py
   ```

5. The login window should appear if the setup is complete.

## Troubleshooting

- **Missing Python module:** Run `python -m pip install package-name`, replacing `package-name` with the missing package.
- **ODBC driver error:** Check that ODBC Driver 17 is installed.
- **Database connection error:** Check that SQL Server is running and that `PDMS_SERVER` matches your instance name.
- **PDMS database not found:** Make sure the database setup script has been run.
- **Cannot log in with an old sample account:** The updated application checks hashed passwords, so old accounts that stored plaintext passwords may not work. Try registering a new account.

## Note

Use fictional test information when trying out the system. Do not upload real patient information, passwords, or database backups to a public repository.
