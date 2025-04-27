import sqlite3
import threading

from dataclasses import dataclass, field


@dataclass
class UserMessages:
    """
    A class to manage user messages using an SQLite database.

    This class allows storing, retrieving, checking, and clearing user messages
    in a thread-safe way, ensuring that data persists between bot restarts.

    Attributes:
        db_path (str): Path to the SQLite database file.
        conn (sqlite3.Connection): SQLite connection object.
        lock (threading.Lock): Lock object to ensure thread safety.
    """
    db_path: str = "user_messages.db"
    conn: sqlite3.Connection = field(init=False, repr=False)
    lock: threading.Lock = field(init=False, repr=False)

    def __post_init__(self):
        """
        Initializes the UserMessageStore and establishes a connection to the SQLite database.
        This method is called automatically after the dataclass is initialized.
        """
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self._create_table()

    def _create_table(self):
        """
        Creates the 'messages' table in the database if it does not already exist.
        """
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL
                )
            ''')
            self.conn.commit()

    def add_message(self, user_id: int, message: str):
        """
        Adds a message to the database for a given user.

        Args:
            user_id (int): The user's unique identifier.
            message (str): The message text to store.
        """
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO messages (user_id, message) VALUES (?, ?)',
                (user_id, message)
            )
            self.conn.commit()

    def get_full_text(self, user_id: int) -> str:
        """
        Retrieves all messages for a given user, concatenated into a single string.

        Args:
            user_id (int): The user's unique identifier.

        Returns:
            str: Concatenated text of all stored messages.
        """
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT message FROM messages WHERE user_id = ?', (user_id,))
            rows = cursor.fetchall()
            messages = [row[0] for row in rows]
            return " ".join(messages)

    def has_messages(self, user_id: int) -> bool:
        """
        Checks whether a user has any stored messages.

        Args:
            user_id (int): The user's unique identifier.

        Returns:
            bool: True if there are any messages, False otherwise.
        """
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT 1 FROM messages WHERE user_id = ? LIMIT 1', (user_id,))
            return cursor.fetchone() is not None

    def clear_messages(self, user_id: int):
        """
        Deletes all messages associated with a given user.

        Args:
            user_id (int): The user's unique identifier.
        """
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM messages WHERE user_id = ?', (user_id,))
            self.conn.commit()

    def close(self):
        """
        Closes the database connection.
        """
        with self.lock:
            self.conn.close()
