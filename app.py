#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
from rag import WelcomeChatBot

# Load environment variables from .env file
load_dotenv()

chatbot = WelcomeChatBot()
chatbot.setup_config()

# Access environment variables
TELEGRAM_KEY = os.environ['TELEGRAM_KEY']

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

COUNTRY, QUESTION = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about the desired country."""
    reply_keyboard = [["Switzerland 🇨🇭", "France 🇫🇷", "Germany 🇩🇪", "Italy 🇮🇹"]]

    await update.message.reply_text(
        "Hello, I'm WelcomeBot, nice to meet you. I'll help you get settled in a new country!\n\n"
        "Select the country you're interested in.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Which country?"
        ),
    )

    return COUNTRY


async def country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected country and asks for questions."""
    user = update.message.from_user
    logger.info(f"Country of {user.first_name} : {update.message.text}")
    await update.message.reply_text(
        f"{update.message.text},  awesome!\n"
        "Tell me, what do you want to know about your installation there?",
        reply_markup=ReplyKeyboardRemove(),
    )
    
    ### INSTANCIER LE MODELE ICI ###

    return QUESTION


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the country and asks for a question."""
    user = update.message.from_user
    logger.info(f"{user} says : {update.message.text}")
    await update.message.reply_text(chatbot.get_answer(update.message.text))

    return QUESTION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_KEY).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COUNTRY: [MessageHandler(filters.Regex("^(Switzerland 🇨🇭|France 🇫🇷|Germany 🇩🇪|Italy 🇮🇹)$"), country)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, question)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()