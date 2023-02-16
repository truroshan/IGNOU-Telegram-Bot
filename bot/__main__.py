from .ignou import Ignou
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.database import Database

db = Database()
client = Ignou()

if __name__ == "__main__":

    # schedular for checking result
    scheduler = AsyncIOScheduler()

    scheduler.add_job(client.tee_crawler, 'cron', day_of_week='0-6', hour="0-19", minute='0-59/20')
    
    scheduler.add_job(client.grade_crawler, 'cron', day_of_week='0-6', hour="0-19", minute='0-59/25')
    
    scheduler.start()
    client.run()