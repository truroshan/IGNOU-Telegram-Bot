from pyrogram import  Client
from pyrogram import  filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message
)

import datetime

from bot.database import Database
from bot.config import Config
from bot.helper.ignouresult import IgnouResult

from bot.helper.extractor import User

db = Database()


# Completed
@Client.on_message(filters.regex('^(m|M)y'))
@Client.on_message(filters.command(['my']))
async def my(_, message):
    user: User = User(await db.get_user(message.from_user.id))

    if 'my' == message.text.lower():
        if user.myenrollment:
            await result_card(_, message)
        else:
            await message.reply_text("Set Your Enrollment using \n my 197xx00xx22")
            return
    else:
        student = message.text.split()
        try:
            await db.update(
                db.user,
                message.from_user.id,
                {"$set": {"myenrollment": student[1] + student[2]}})

            await message.reply_text("Data Saved Successfully ")
        except IndexError:
            await message.reply_text("First Set your Enrollment using \n my course_code enrollment")


# Completed
@Client.on_message(filters.regex("^\D+\d{8,10}") | filters.regex("^\d{8,10}"))
async def result_card(_, message: Message):
    get_course = False
    user: User = User(await db.get_user(message.from_user.id))

    if message.text.isnumeric():
        if not user.course:
            await message.reply("You must check once result with Course code \n example : bca 197xx00xx22")
            return
        else:
            get_course = user.course
    # elif 'my' in message.text.lower() or 'last' in message.text.lower():
    #     user: User = await db.get_user(message.from_user.id)

    result_query = ''
    if get_course:
        result_query = get_course + message.text
    elif 'my' in message.text.lower():
        result_query = user.myenrollment
    elif "last" in message.text.lower():
        result_query = user.course + user.enrollment
    else:
        result_query = message.text

    student: IgnouResult = IgnouResult(result_query)
    result = student.gradeResultString()

    if not result:
        await message.reply_text('Enrollment no is not correct or \nGrade Card Site is Down 🤕')
        return

    if not user.following.get(student.enrollmentNo):
        inline_keyboard = InlineKeyboardMarkup(
            [
                [  # First row
                    InlineKeyboardButton(  # Generates a callback query when pressed
                        "Add to Watch List 👀",
                        callback_data=f"add_{student.courseId}_{student.enrollmentNo}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Share this 🤖",
                        switch_inline_query=f"\nTry this Easy IGNOU Bot\n 👉🏻 {Config.USERNAME} \n\n Created by @r0sh7n"
                    )
                ]
            ]
        )
    else:
        inline_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Share this 🤖",
                        switch_inline_query=f"\nTry this Easy IGNOU Bot\n 👉🏻 {Config.USERNAME} \n Created by @r0sh7n"
                    )
                ]
            ]
        )

    await message.reply_text(
        result.get("result", '') + Config.FOOTER_CREDIT,
        parse_mode='html',
        reply_markup=inline_keyboard)

    await db.update_last_action(
        message.from_user.id,
        {"course": student.courseId, "enrollment": student.enrollmentNo})

    # Tee Result Card
    result: IgnouResult = IgnouResult(result_query).teeResultString()
    if result:
        await message.reply_text(
            result.get("result", '') + Config.FOOTER_CREDIT,
            parse_mode='html')


@Client.on_callback_query(filters.regex("^add") | filters.regex("^remove"))
async def watch_list(_, callback_query: CallbackQuery):
    """
    callback_query example:
        add_bca_192112313
        remove_bca_1092313
    """
    _, course, enrollment = callback_query.data.split("_")

    today_date = datetime.datetime.today().strftime('%B %d, %Y')

    # info about follower who is following enrollment
    user_dict = {
        "username": callback_query.from_user.username,
        "name": callback_query.from_user.first_name,
        "_id": callback_query.from_user.id,
        "added_on": datetime.date.today().isoformat()
    }

    # add enrollment in following list
    if 'add' in callback_query.data:

        # Grade Card
        student = IgnouResult(course + enrollment)
        result = student.gradeResultJson()

        # if unable to fetch result from ignou site
        if result.get("status") != "ok":
            await callback_query.answer("Unable to fetch details\nTry after sometime ", show_alert=True)
            return

        # student data
        student_info = result.get("student", {})

        # result pass fail in dict(passed,failed)
        count = result.get("count", {})

        # student info in user following section
        await db.update(
            db.user,
            callback_query.from_user.id,
            {
                "$set": {
                    f"following.{enrollment}": {
                        "name": student_info.get("name"),
                        "course": student_info.get("course")
                    }
                }
            })

        # this dict gonna update in crawler db
        info_dict = {
            "_id": enrollment
        }

        # check if student is already in crawler db
        if not await db.find(
                db.crawler,
                enrollment
        ):
            # collection info then update in info_dict : Dict variable
            student_db = {
                "name": student_info.get("name", ""),
                "course": course,
                "grade": {
                    "count": {
                        "passed": count.get("passed", 0),
                        "failed": count.get("failed", 0)
                    },
                    "checked": today_date
                },
            }

            # updating info_dict : Dict with student_db
            info_dict.update(student_db)

            # Tee Card Json
            result = student.teeResultJson()

            # list of out result in tee
            count = result.get("count", 0)

            # this for tee section in crawler
            student_db = {
                "tee": {
                    "count": count or 0,
                    "checked": today_date
                },
            }

            # updating again info_dict with new tee student_db
            info_dict.update(student_db)

            # adding follower info in info_dict
            info_dict.update(
                {
                    "followers": {
                        str(callback_query.from_user.id): user_dict
                    }
                }
            )

            # inserting first time student in crawlre db
            await db.insert(
                db.crawler,
                info_dict
            )

        # if student is already in crawler db then
        # just update following and followers secion
        # in user db in crawler db
        else:
            await db.update(
                db.crawler,
                enrollment,
                {
                    "$set": {
                        f"followers.{callback_query.from_user.id}": user_dict}
                })

        # remove inline_button from result
        await callback_query.edit_message_reply_markup()
        # push notification to user
        await callback_query.answer(
            f"{student_info.get('name')} Added in Watch List 🙃\n😇You will automatically receive result once it published in IGNOU 🌐", 
            show_alert=True)

    # this conditon for remove followed user
    # from crawler followers section and in user following section
    elif "remove" in callback_query.data:

        await db.update(
            db.user,
            callback_query.from_user.id,
            {
                "$unset": {
                    f"following.{enrollment}": ""
                }
            })
        await db.update(
            db.crawler,
            enrollment,
            {
                "$unset": {
                    f"followers.{callback_query.from_user.id}": ""
                }
            }
        )
        await callback_query.answer("User Removed from Watchlist 👀")
