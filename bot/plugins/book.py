from pyrogram import Client
from pyrogram import filters

from bot.helper.ignoubooks import IgnouBooks
from bot.config import Config

# Completed Add DB Support
@Client.on_message(filters.command(['book']) & filters.chat(Config.SUDO_CHAT))
def books(client: Client, message):
    text = message.text
    try:
        course_code = text.split(" ")[1].upper()
        subject_code = text.split(" ")[2].upper()
    except IndexError:
        message.reply_text('Wrong Course Name or Subject Code 😐')
        return

    if books.find_one(subject_code):
        # add code for database books for sending from cache
        pass

    if subject_code.upper() == 'LIST':
        message.reply_text(IgnouBooks(course=course_code).get_courseSubjectlist())
    else:
        message.reply_text("please wait.. sending books")
        files = IgnouBooks(course=course_code, subject=subject_code).getDownload()
        for file in files:
            client.send_document(
                message.
                    chat,
                id,
                file,
                caption=f'Downloaded using {Config.USERNAME}')
