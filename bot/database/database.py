import datetime

import motor.motor_asyncio

from bot.config import Config


class Singleton(type):
    __instances__ = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances__:
            cls.__instances__[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls.__instances__[cls]


class Database(metaclass=Singleton):
    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(Config.DATABASE_URL)
        self.db = self._client[Config.SESSION_NAME]

        self.user = self.db.user
        self.crawler = self.db.crawler
        self.site = self.db.site

    async  def get_student(self, _id):
        return await self.crawler.find_one({"_id" : _id})

    async def get_user(self, id):

        user = await self.user.find_one({"_id": id})
        return user

    def get_time(self):
        return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    async def add_user(self, _id, name):

        user = dict(
            _id=_id,
            name = name,
            join_date=datetime.date.today().isoformat(),
            action = dict(
                last_used_on=self.get_time(),
            ),
            role_status=dict(
                is_admin = False
            )
        )
        await self.user.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.get_user(id)
        return True if user else False

    async def total_users_count(self):
        count = await self.user.count_documents({})
        return count

    async def total_crawlers_count(self):
        count = await self.crawler.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.user.find({})
        return all_users

    async def get_all_crawlers(self):
        all_users = self.crawler.find({})
        return all_users

    async def get_last_used_on(self, _id):
        user = await self.get_user(_id)
        return user.get("last_used_on", datetime.date.today().isoformat())

    # Last Used Time
    async def update_last_used_on(self, _id):
        await self.user.update_one(
            {"_id": _id}, {"$set": {"action.last_used_on": self.get_time()}}
        )

    # Get When Last Time Used
    async def get_last_used_on(self, _id):
        user = await self.get_user(_id)
        return user.last_used_on

    # Last Action
    async def update_last_action(self,_id, query):
        query['last_used_on'] = self.get_time()
        self.user.update_one(
            {"_id": _id},
            {"$set": {"action": query}})

    async def update(self,col, _id, info_dict):
        await col.update_one(
            {"_id" : _id},
            info_dict)

    async def find(self, col,_id,info_dict = {}):
        return await col.find_one(
            {"_id" : _id },
            info_dict)

    async def insert(self, col, info_dict):
        return await col.insert_one(info_dict)

    async def get_site_update(self,site):
        site_update = await self.site.find_one({"_id": site})

        if site_update is None:
            await self.site.insert_one({"_id": site})
            return {}
        return site_update
