import os
import threading
import unittest

from src.user_messages import UserMessages


class TestUserMessages(unittest.TestCase):
    def setUp(self):
        """Create a UserMessages object before each test."""
        self.db_path = "test_user_messages.db"
        self.user_messages = UserMessages(db_path=self.db_path)

    def tearDown(self):
        """Close the database connection and remove the database file after each test."""
        self.user_messages.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_message(self):
        """Test adding a message."""
        self.user_messages.add_message(1, "Hello!")
        full_text = self.user_messages.get_full_text(1)
        self.assertIn("Hello!", full_text)

    def test_get_full_text(self):
        """Test getting all messages for a user."""
        self.user_messages.add_message(1, "Hello!")
        self.user_messages.add_message(1, "How are you?")
        full_text = self.user_messages.get_full_text(1)
        self.assertEqual(full_text, "Hello! How are you?")

    def test_has_messages(self):
        """Test checking if a user has messages."""
        self.user_messages.add_message(1, "Hello!")
        has_msgs = self.user_messages.has_messages(1)
        self.assertTrue(has_msgs)

        # Check after clearing messages
        self.user_messages.clear_messages(1)
        has_msgs = self.user_messages.has_messages(1)
        self.assertFalse(has_msgs)

    def test_clear_messages(self):
        """Test clearing messages for a user."""
        self.user_messages.add_message(1, "Hello!")
        self.user_messages.clear_messages(1)
        has_msgs = self.user_messages.has_messages(1)
        self.assertFalse(has_msgs)

    def test_thread_safety(self):
        """Test thread-safety (concurrent access)."""
        def add_messages():
            for i in range(5):
                self.user_messages.add_message(i, f"Message {i}")

        def check_messages():
            for i in range(5):
                full_text = self.user_messages.get_full_text(i)
                self.assertIn(f"Message {i}", full_text)

        threads = []
        for _ in range(5):  # Create multiple threads to add and retrieve messages
            t1 = threading.Thread(target=add_messages)
            t2 = threading.Thread(target=check_messages)
            threads.append(t1)
            threads.append(t2)

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all threads to finish
        for t in threads:
            t.join()

    def test_multiple_users(self):
        """Test working with multiple users."""
        self.user_messages.add_message(1, "Hello from user 1!")
        self.user_messages.add_message(2, "Hello from user 2!")

        full_text_1 = self.user_messages.get_full_text(1)
        full_text_2 = self.user_messages.get_full_text(2)

        self.assertEqual(full_text_1, "Hello from user 1!")
        self.assertEqual(full_text_2, "Hello from user 2!")


def test_database():
    unittest.main()
