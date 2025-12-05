"""
Configuration for Telegram Bot
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Bot configuration"""

    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Backend API
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://prodentai:prodentai_password@localhost:5432/prodentai",
    )

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Bot settings
    MAX_MESSAGE_LENGTH = 4096
    POLLING_INTERVAL = 1.0

    @classmethod
    def get_api_endpoints(cls):
        """Get API endpoints with current BACKEND_URL"""
        backend_url = cls.BACKEND_URL or "http://localhost:8000"
        return {
            "auth": f"{backend_url}/api/auth",
            "users": f"{backend_url}/api/users",
            "risks": f"{backend_url}/api/risks",
            "nutrition": f"{backend_url}/api/nutrition",
            "psychology": f"{backend_url}/api/psychology",
            "reminders": f"{backend_url}/api/reminders",
            "facts": f"{backend_url}/api/facts",
        }


# Initialize API endpoints after Config class is defined
Config.API_ENDPOINTS = Config.get_api_endpoints()
