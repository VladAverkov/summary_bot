import unittest
from unittest.mock import AsyncMock, MagicMock

from src.summary_bot import SummaryBot


class TestSummaryBot(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Create a mock model and mock UserMessages
        self.mock_model = MagicMock()
        self.mock_model.summarize.return_value = "summarized text"

        self.mock_message_store = MagicMock()
        self.mock_message_store.has_messages.return_value = True
        self.mock_message_store.get_full_text.return_value = "full text"
        self.mock_message_store.clear_messages = MagicMock()

        # Initialize the bot with mocks
        self.bot = SummaryBot(
            token="dummy-token",
            model=self.mock_model,
            db_path=":memory:"  # in-memory DB
        )
        # Replace real message store with a mock
        self.bot.message_store = self.mock_message_store

    async def test_start_command(self):
        """Test that /start command sends the welcome message."""
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        await self.bot.start(update, context)

        update.message.reply_text.assert_awaited_once_with(self.bot.WELCOME_MESSAGE)

    async def test_handle_message_stores_message_and_sends_notification(self):
        """Test that a user message is stored and a notification is sent."""
        update = MagicMock()
        update.message.from_user.id = 123
        update.message.text = "Hello, bot!"
        update.message.reply_text = AsyncMock(return_value=MagicMock(message_id=42))

        context = MagicMock()
        context.bot.delete_message = AsyncMock()

        await self.bot.handle_message(update, context)

        self.mock_message_store.add_message.assert_called_once_with(123, "Hello, bot!")
        update.message.reply_text.assert_awaited()
        self.assertEqual(self.bot.last_message_id[123], 42)

    async def test_summarize_without_messages(self):
        """Test /summarize when user has no messages."""
        self.mock_message_store.has_messages.return_value = False

        update = MagicMock()
        update.message.from_user.id = 123
        update.message.reply_text = AsyncMock()

        context = MagicMock()

        await self.bot.summarize(update, context)

        update.message.reply_text.assert_awaited_with(
            "You don't have any messages yet. Send me something!"
        )

    async def test_summarize_with_messages(self):
        """Test /summarize when user has messages."""
        update = MagicMock()
        update.message.from_user.id = 123
        update.message.reply_text = AsyncMock()
        update.effective_chat.id = 12345

        context = MagicMock()
        context.bot.delete_message = AsyncMock()

        # Simulate a previous notification
        self.bot.last_message_id[123] = 42

        await self.bot.summarize(update, context)

        self.mock_model.summarize.assert_called_once_with("full text")
        update.message.reply_text.assert_awaited_with("summarized text")
        self.mock_message_store.clear_messages.assert_called_once_with(123)
        context.bot.delete_message.assert_awaited_once_with(chat_id=12345, message_id=42)
