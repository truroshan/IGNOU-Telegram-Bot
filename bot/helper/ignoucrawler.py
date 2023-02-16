import asyncio
from bot.helper.ignouresult import IgnouResult
from bot.database import Database
from bot.helper.extractor import Student
import datetime
import time

from pyrogram import Client
from pyrogram.errors import FloodWait,PeerIdInvalid

db = Database()


class IgnouCrawler:

    def __init__(self,client) -> None:

        self.db = db
        self.client = client

        self.greeted = {
            "grade" : {},
            "tee" : {}
        }
        self.greet_msg = {
            "grade" : "Grade Card Updated Today ",
            "tee" : "One more result out Today 🤒"
        }

        self.todayDate = datetime.datetime.today().strftime('%B %d, %Y')

    async def greet_user(self, result_type, user_id):

        if not self.greeted.get(result_type).get(user_id):
            self.greeted[result_type][user_id] = True
            try:
                await self.client.send_message(
                    user_id,
                    f"<b>{self.greet_msg.get(result_type)}👩🏻‍🎨</b>",parse_mode='html')
            except FloodWait as e:
                time.sleep(e.x)
                await self.client.send_message(
                    user_id,
                    f"<b>{self.greet_msg.get(result_type)}👩🏻‍🎨</b>",parse_mode='html')
            except PeerIdInvalid as e:
                print(f"{user_id} -> {e}")

    async def teeCrawl(self, student: Student):

        data = IgnouResult('roshan'+ student._id).teeResultString()

        if data and student.tee.count != data.get("count"):

            title = '<pre>' + f'Name : {student.name} -> {student.course}\n' + '</pre>'

            for user_id in student.followers:

                if not self.greeted.get("tee").get(user_id):
                    await self.greet_user("tee", user_id)

                try:
                    await self.client.send_message(
                        chat_id=user_id,
                        text= title + data.get("result"),
                        parse_mode='html')

                except FloodWait as e:
                    time.sleep(e.x)
                    await self.client.send_message(
                        chat_id=user_id,
                        text= title + data.get("result"),
                        parse_mode='html')
                except PeerIdInvalid as e:
                    print(f"{user_id} -> {e}")

            await self.db.update(
                self.db.crawler,
                student._id,
                {
                    "$set": {
                        "tee.count": data.get("count"),
                        "tee.checked": self.todayDate
                    }
                }
            )

    async def teeTask(self):

        print("Tee Result Crawling : {}".format(datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")))

        await self.db.update(
            self.db.site,
            "ignou",
            {
                "$set" : {
                    "tee_checked": datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
                }
            }
        )

        tasks = []

        students = await db.get_all_crawlers()
        self.greeted['tee'] = {}

        # Check first TEE SIte Updated or not
        site = await IgnouResult().teeCardUpdated()
        if not site.get("updated"):
            # print("Tee card Site not Updated")
            return

        # if site updated check for results
        async for student in students:
            student_info = Student(student)

            if student_info.tee.checked == self.todayDate:
                continue

            tasks.append(
                    asyncio.create_task(
                        self.teeCrawl(student_info)
                    )
                )

        await asyncio.gather(*tasks)

        await self.db.update(
            self.db.site,
            "ignou",
            {
                "$set" : {
                    "tee" : site.get("date"),
                    "tee_checked": datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
                }
            }
        )

    async def gradeCrawl(self,student: Student):

        data = IgnouResult(student.course + student._id).gradeResultString()

        grade_passed = data.get("json", {}).get("count", {}).get("passed", 0)
        grade_failed = data.get("json", {}).get("count", {}).get("failed", 0)

        if data and (int(student.grade.passed) !=  grade_passed or int(student.grade.failed) != grade_failed) or True:

            for user_id in student.followers:

                if not self.greeted.get("grade").get(user_id):
                    await self.greet_user("grade", user_id)

                try:
                    await self.client.send_message(
                        chat_id= user_id,
                        text = data.get("result"),
                        parse_mode ='html')

                except FloodWait as e:
                    time.sleep(e.x)
                    await self.client.send_message(
                        chat_id= user_id,
                        text = data.get("result"),
                        parse_mode ='html')
                except PeerIdInvalid as e:
                    print(f"{user_id} -> {e}")

            await self.db.update(
                self.db.crawler,
                student._id,
                {
                    "$set" : {
                        "grade.count.passed": grade_passed,
                        "grade.count.failed": grade_failed,
                        "grade.checked": self.todayDate
                        }
                }
            )

    async def gradeTask(self):
        print("Grade Card Crawling : {}".format(datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")))

        await self.db.update(
            self.db.site,
            "ignou",
            {
                "$set": {
                    "grade_checked": datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
                }
            }
        )

        tasks = []

        students = await db.get_all_crawlers()
        self.greeted['grade'] = {}

        # Check first Grade Site Updated or not
        site = await IgnouResult().gradeCardUpdated()
        if not site.get("updated"):
            # print("Grade card Site not Updated")
            return

        # if site updated check for results

        async for student in students:
            student_info = Student(student)

            if student_info.grade.checked == self.todayDate:
                continue

            tasks.append(
                    asyncio.create_task(
                        self.gradeCrawl(student_info)
                    )
                )

        await asyncio.gather(*tasks)

        await self.db.update(
            self.db.site,
            "ignou",
            {
                "$set" : {
                    "grade": site.get("date"),
                    "grade_checked": datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
                }
            }
        )


if __name__ == "__main__":
    pass

