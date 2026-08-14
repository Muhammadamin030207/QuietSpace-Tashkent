import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
MINIAPP_URL = os.getenv("MINIAPP_URL", "http://localhost:5173")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
BOT_WEBHOOK_MODE = os.getenv("BOT_WEBHOOK_MODE", "false").lower() == "true"
BOT_WEBHOOK_PATH = os.getenv("BOT_WEBHOOK_PATH", "/telegram/webhook")
BOT_WEBHOOK_HOST = os.getenv("BOT_WEBHOOK_HOST", "0.0.0.0")
BOT_WEBHOOK_PORT = int(os.getenv("BOT_WEBHOOK_PORT", "8443"))