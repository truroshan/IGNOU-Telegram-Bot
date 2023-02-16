from pyrogram import Client
from bot.config import Config
from bot.helper.ignoucrawler import IgnouCrawler




class Ignou(Client):
    def __init__(self):
        super().__init__(
            session_name=Config.SESSION_NAME,
            bot_token=Config.BOT_TOKEN,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins=dict(root="bot/plugins"),
        )

        self.IgnouCrawler = IgnouCrawler(self)

    async def grade_crawler(self):
        await self.IgnouCrawler.gradeTask()

    async def tee_crawler(self):
        await self.IgnouCrawler.teeTask()