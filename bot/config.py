import os

class Config:
    NAME = "IGNOU"
    USERNAME = os.environ.get("USERNAME")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    API_ID = os.environ.get("API_ID")
    API_HASH = os.environ.get("API_HASH")
    SUDO_CHAT = os.environ.get("SUDO_CHAT")
    SUDO_ADMIN = os.environ.get("SUDO_ADMIN","").split(",")
    DATABASE_URL = os.environ.get("DB_URL","localhost:27017")
    SESSION_NAME = os.environ.get("SESSION_NAME")
    FOOTER_CREDIT = f"\n<b>Result fetched using {USERNAME}</b>"
    HELP_URL = os.environ.get("HELP_URL")

