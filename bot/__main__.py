import os

from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode

from .ignou import IgnouResult, ResultNotFoundError

try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
except KeyError:
    print("BOT_TOKEN not found in environment variables.")
    exit(1)


app = Client(
    ":ignou:",
    api_id=os.environ.get("API_ID", "21724"),
    api_hash=os.environ.get("API_HASH", "3e0cb5efcd52300aec5994fdfc5bdc16"),
    bot_token=BOT_TOKEN,
    in_memory=True
)

ignou = IgnouResult()


@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        f"Hi {message.from_user.mention}!\nSend me your program code with enrollment number to get your grade card result.",
    )


@app.on_message(filters.regex(r"([a-zA-z]+)\s*?(\d+$)"))
async def get_grade_result(_, message):

    if message.chat.type == ChatType.GROUP or message.chat.type == ChatType.SUPERGROUP:
        await message.delete()

    program_id, enrollment_no = message.matches[0].groups()

    try:
        footer = f"<strong>Result checked by {message.from_user.mention(message.from_user.first_name)}</strong>"
    except AttributeError:
        footer = ""

    try:
        result = await ignou.gradeResultData(program_id, enrollment_no)
    except ResultNotFoundError:
        await message.reply_text("Grade Card Result not found.")
        return

    if message.chat.type == ChatType.GROUP or message.chat.type == ChatType.SUPERGROUP:
        await message.reply_text(
            f"<pre>{result['table']}</pre>\n{footer}",
            parse_mode=ParseMode.HTML,
        )
    elif message.chat.type == ChatType.PRIVATE:
        await message.reply_text(
            f"<pre>{result['header']}{result['table']}</pre>",
            parse_mode=ParseMode.HTML,
        )


if __name__ == "__main__":
    app.run()
