import argparse

from src.summary_bot import SummaryBot
from src.summary_model import SummaryModel


def parse_args():
    parser = argparse.ArgumentParser(description="Run SummaryBot")
    parser.add_argument("api_token", help="Telegram API token")
    parser.add_argument("--max-input-length", default=500, help="Maximum length of input text per batch (the text is divided into blocks of this size, and each block is then passed to the model)")
    parser.add_argument("--model-name", default="t5-small", help="Name of the model to use")
    parser.add_argument("--db-path", default="user_messages.db", help="Path to the database file")
    return parser.parse_args()


def run_app():
    args = parse_args()

    model = SummaryModel(args.model_name, args.max_input_length)
    bot = SummaryBot(args.api_token, model, args.db_path)
    bot.run()


if __name__ == "__main__":
    run_app()
