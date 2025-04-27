import logging
from dataclasses import dataclass

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from .user_messages import UserMessages
from .summary_model import SummaryModel


@dataclass
class SummaryBot:
    token: str
    model: SummaryModel
    db_path: str = "user_messages.db"
    message_store: UserMessages = None
    app: ApplicationBuilder = None
    last_message_id: dict = None  # Store the ID of the last notification message

    def __post_init__(self):
        self.app = ApplicationBuilder().token(self.token).build()
        self.message_store = UserMessages(db_path=self.db_path)
        self.last_message_id = {}  # Initialize the dictionary
        self._setup_handlers()

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("summarize", self.summarize))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(self.WELCOME_MESSAGE)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        text = update.message.text

        self.message_store.add_message(user_id, text)

        # Delete the previous notification if it exists
        if user_id in self.last_message_id:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=self.last_message_id[user_id])
            except Exception as e:
                logging.warning(f"Failed to delete previous message for user {user_id}: {e}")

        # Send a new notification
        sent_message = await update.message.reply_text(
            "Message received! ✅\n"
            "When you're ready, send /summarize and I will compress the content."
        )

        # Store the ID of the new notification
        self.last_message_id[user_id] = sent_message.message_id

    async def summarize(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id

        if not self.message_store.has_messages(user_id):
            await update.message.reply_text(
                "You don't have any messages yet. Send me something!"
            )
            return

        full_text = self.message_store.get_full_text(user_id)

        # Use the real summarization model here
        summarized_text = self.model.summarize(full_text)

        await update.message.reply_text(summarized_text)

        self.message_store.clear_messages(user_id)

        # After summarization, delete the notification if it still exists
        if user_id in self.last_message_id:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=self.last_message_id[user_id])
                del self.last_message_id[user_id]
            except Exception as e:
                logging.warning(f"Failed to delete summary notification for user {user_id}: {e}")

    def run(self):
        logging.info("Bot is running...")
        self.app.run_polling()

    def stop(self):
        self.message_store.close()

    WELCOME_MESSAGE: str = (
        "Hi, I'm zip-zip! 📦\n"
        "Send me your messages or texts, and I will summarize them into a short version."
    )
