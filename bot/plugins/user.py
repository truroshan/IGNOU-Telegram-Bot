import re

from pyrogram import Client
from pyrogram import filters

from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message
)

from bot.database import Database
from bot.helper.extractor import User, Student
from bot.config import Config
from bot.plugins.result import result_card

db = Database()


@Client.on_message(filters.command(['start', 'help']))
async def start(_, message):
    if 'start' in message.text.lower():

        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)

        await message.reply_text(f"Welcome , {message.from_user.first_name} 🥳 \n \
        [Click here for more details 🔍]({Config.HELP_URL})", disable_web_page_preview=True)

    elif 'help' in message.text.lower():

        await message.reply_text(f"{Config.HELP_URL}")

    await db.update_last_used_on(message.from_user.id)

@Client.on_message(filters.command(["stats"]))
async def stats(client: Client,message : Message):

    user: User = User(await db.get_user(message.from_user.id))
    total_user = await db.total_users_count()
    total_crawler = await db.total_crawlers_count()
    total_following = len(user.following)

    msg = f"""
Hi, {message.from_user.first_name}

Your Stat 🙃
    TG 🆔 : {message.from_user.id}
    Following 🕵️  : {total_following}
"""
    if user.is_admin or message.from_user.id in Config.SUDO_ADMIN:
        try:
            user_enrollment_not = re.findall("\d+",user.myenrollment)[0]
            user_crawler_info: Student = Student(await db.get_student(user_enrollment_not))
            msg += f"    Followers 👼 : {len(user_crawler_info.followers)}\n"
        except (IndexError, AttributeError, TypeError):
            pass

    site_info = await db.get_site_update("ignou")
    grade_checked = site_info.get("grade_checked","error in monitoring")
    tee_checked = site_info.get("tee_checked","error in monitoring ")

    msg += f"""
{Config.USERNAME} Stat 🤖
    Total User  🙆: {total_user}
    Result Monitoring 😎: {total_crawler}

👀 Last Grade Card Checked
    🕗 -> {grade_checked}

Last Tee Result Check
    🕗 -> {tee_checked}
"""
    await message.reply_text(msg)


@Client.on_callback_query(filters.regex("^user"))
async def user_info(_, callback_query: CallbackQuery):
    _, enrollment = callback_query.data.split("_")

    user: User = User(await db.get_user(callback_query.from_user.id))

    student: Student = Student(await db.find(
        db.crawler,
        enrollment,
        {"_id" : 0}
    ))

    followed_by = len(student.followers)

    msg_string = f"""👩🏻‍🎓 {student.name}    
    🆔 {enrollment} ({student.course})
    Grade Card : ✝️ {student.grade.passed+student.grade.failed} ✅ {student.grade.passed} ❎ {student.grade.failed} 
    Grade Card Updated on {student.grade.checked}   
    """
    if user.is_admin or callback_query.from_user.id in Config.SUDO_ADMIN:
        msg_string += f"Followed by {followed_by} 👀"

    await callback_query.answer(msg_string, show_alert=True)


@Client.on_message(filters.command(['watchlist']))
async def followed_list(_, message: Message):
    user: User = User(await db.get_user(message.from_user.id))

    if len(user.following) == 0:
        await message.reply_text("Not followed anyone")
        return

    buttons = []
    for enrollment, usr in user.following.items():
        row = [
                InlineKeyboardButton(
                    usr.get("name").split()[0],
                    callback_data=f"user_{enrollment}"
                ),
                InlineKeyboardButton(
                    "🗑",
                    callback_data=f"remove_{usr.get('course')}_{enrollment}"
                ),
            ]

        buttons.append(
            row
        )
    await message.reply_text(
        "<b>👩🏻‍🎓 Users in 👀 Watchlist</b>", 
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="html")


@Client.on_message(filters.command(['last']))
async def last_result_check(_, message):
    user: User = User(await db.get_user(message.from_user.id))

    if user.enrollment:
        await result_card(_, message)
    else:
        await message.reply_text("No recent result checked")

