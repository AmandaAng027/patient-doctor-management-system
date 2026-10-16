import os
import pyodbc

class DataAccessLayer:
    """
    Manages connections and transactions to the Microsoft SQL Server database.
    This version uses the successful connection string format identified by the user.
    """

    SERVER = os.getenv("PDMS_SERVER", r"localhost\SQLEXPRESS")

    CONNECTION_STRING = (
        "Driver={ODBC Driver 17 for SQL Server};"
        f"Server={SERVER};"
        "Database=PDMS;"
        "Trusted_Connection=yes;"
    )

    def __init__(self):
        """Initialize DataAccessLayer instance"""
        self.conn = None
        self.cursor = None

    def open(self):
        """Opens the database connection"""
        try:
            self.conn = pyodbc.connect(DataAccessLayer.CONNECTION_STRING)
            self.cursor = self.conn.cursor()
            return True
        except pyodbc.Error as ex:
            raise Exception(f"Connection failed: SQL Server error during open: {str(ex)}")

    def close(self):
        """Closes the database connection"""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None

    def commit(self):
        """Commits the current transaction"""
        if self.conn:
            self.conn.commit()

    def rollback(self):
        """Rolls back the current transaction"""
        if self.conn:
            self.conn.rollback()

    def execute(self, sql_query, *params):
        """Executes a non-query command"""
        if not self.cursor:
            raise Exception("Database connection is not open.")
        self.cursor.execute(sql_query, params)
        return self.cursor.rowcount

    def execute_query(self, sql_query, *params):
        """Executes a query and returns all rows"""
        if not self.cursor:
            raise Exception("Database connection is not open.")
        self.cursor.execute(sql_query, params)
        return self.cursor.fetchall()

    def fetch_one(self, sql_query, *params):
        """Executes a query and returns the first value of the first row"""
        if not self.cursor:
            raise Exception("Database connection is not open.")
        self.cursor.execute(sql_query, params)
        result = self.cursor.fetchone()
        return result[0] if result and len(result) > 0 else None