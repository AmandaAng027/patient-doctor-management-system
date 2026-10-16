# Minimum System Specifications


## Hardware Requirements

- **Operating System:** 64-bit Windows 10 or Windows 11
- **Processor (CPU):** 1.4 GHz dual-core processor or equivalent
- **Memory (RAM):** 4 GB minimum; 8 GB recommended
- **Storage:** At least 1 GB of free space for the application files. Additional space is needed for SQL Server and database files.
- **Display:** 1280 × 720 resolution or higher

## Software Requirements

- **Python:** Python 3.13.5 was used to develop and test the application.
- **Database Engine:** Microsoft SQL Server 2022
- **Database Management Tool:** SQL Server Management Studio (SSMS) 20.2.30.0
- **Database Driver:** Microsoft ODBC Driver 17 for SQL Server

## Notes

The specifications above are the minimum or recommended setup for running the PDMS project. Performance may vary depending on the computer and the amount of data stored in the database. The listed software versions are the versions used during development and testing.
"""
path = Path("/mnt/data/System_Specifications.md")
path.write_text(content, encoding="utf-8")
print(f"Created: {path}")