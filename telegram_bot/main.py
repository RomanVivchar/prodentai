"""
ProDentAI Telegram Bot
Main bot application
"""

import asyncio
import logging
import os

from config import Config
from database import init_db
from dotenv import load_dotenv
from handlers import (  # nutrition_handler,  # Закомментировано - анализ питания отключен
    button_callback_handler,
    facts_handler,
    help_handler,
    message_handler,
    psychology_handler,
    reminders_handler,
    start_handler,
)
from scheduler import reminder_scheduler
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Main bot function"""
    # Check if token is set
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables!")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")

    # Create application
    application = (
        Application.builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("menu", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    # application.add_handler(CommandHandler("nutrition", nutrition_handler))  # Закомментировано - анализ питания отключен
    application.add_handler(CommandHandler("psychology", psychology_handler))
    application.add_handler(CommandHandler("reminders", reminders_handler))
    application.add_handler(CommandHandler("fact", facts_handler))

    # Callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback_handler))

    # Message handler for text messages
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )

    # Закомментировано - анализ питания отключен
    # # Photo handler for nutrition analysis
    # from handlers.main import photo_handler
    # application.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    # Start bot
    logger.info("Starting ProDentAI Telegram Bot...")
    application.run_polling(drop_pending_updates=True)


async def post_init(application: Application) -> None:
    """Initialize database after application starts and start reminder scheduler"""
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(
            f"Database initialization failed: {e}. Bot will continue without database."
        )

    # Start reminder scheduler in background
    bot = application.bot
    logger.info("Starting reminder scheduler...")
    asyncio.create_task(reminder_scheduler(bot))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise
