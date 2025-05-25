import sqlite3


class Database:
    def __init__(self, db_name: str):
        """Initialize the database connection."""
        self.connection = sqlite3.connect(db_name)

    def execute_query(self, query: str, params: tuple = ()):
        """Execute a SQL query on the database."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetch_one(self, query: str, params: tuple = ()):
        """Fetch a single row from the database."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

