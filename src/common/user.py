import hashlib
import os
import sqlite3

from src.common.database import Database
from src.common.jwt import JWT
from src.custom_types.user import UserModel


class User:
    def __init__(self):
        self.db_name = "users.db"
        self._init_db() # Creates the database if it doesn't exist
        self.database = Database(self.db_name)
        self.jwt = JWT("random")

    def _init_db(self) -> None:
        """Create the SQLite database if it doesn't exist."""
        # Check if the database file exists
        if not os.path.exists(self.db_name):
            print(f"Database '{self.db_name}' does not exist. Creating it...")
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            # Create the users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    diet_preference TEXT CHECK(diet_preference IN ('veg', 'non-veg')) NOT NULL
                )
            """)
            connection.commit()
            connection.close()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, user: UserModel) -> bool:
        """Register a new user with a hashed password."""
        try:
            hashed_password = self.hash_password(user.password)
            self.database.execute_query(
                "INSERT INTO users (username, password, first_name, last_name, weight, height, diet_preference) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user.username, hashed_password, user.first_name, user.last_name, user.weight, user.height, user.diet_preference)
            )
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists

    def authenticate(self, username: str, password: str) -> str | None:
        """Authenticate a user by verifying the username and password."""
        hashed_password = self.hash_password(password)
        user = self.database.fetch_one(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        if user:
            # Optionally, generate a JWT token upon successful authentication
            token = self.jwt.encode(username)
            return token
        else:
            return None

# Uncomment to test the User class functionality
# if __name__ == "__main__":
#     user = User()

#     sampleUser = UserModel(
#         username="testuser",
#         password="testpassword",
#         first_name="Test",
#         last_name="User",
#         weight=70.0,
#         height=175.0,
#         diet_preference="veg"
#     )

#     print(user.register(sampleUser))

#     if user.authenticate("testuser", "testpassword"):
#         print("User authenticated successfully.")
#     else:
#         print("Authentication failed.")

#     if user.authenticate("testuser", "sadf"):
#         print("User authenticated successfully.")
#     else:
#         print("Authentication failed.")

#     if user.authenticate("testuser1", "sadf"):
#         print("User authenticated successfully.")
#     else:
#         print("Authentication failed.")