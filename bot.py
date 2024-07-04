import os
from datetime import date
import logging

import dotenv
from telethon import TelegramClient, events

dotenv.load_dotenv()

from keppler.models import db
from keppler.utils import setup_db, teardown_db
from keppler.handlers import handle_command, handle_message, ActionExecutor

logging.basicConfig(
    filename="logs/bot-{today}.log".format(today=date.today().isoformat()),
    filemode="a",
)
logger = logging.getLogger("bot")

bot = TelegramClient(
    "bot",
    api_id=os.environ["TG_API_ID"],
    api_hash=os.environ["TG_API_HASH"],
    base_logger=logger,
)


@bot.on(events.NewMessage)
async def handle_incoming_message(event: events.NewMessage.Event):
    text = event.text

    if text.startswith("/") and text != "/start":
        msg, keyboard = await handle_command(text, event.sender_id)
    else:
        msg, keyboard = await handle_message(text, event.sender_id)

    await bot.send_message(
        event.chat_id,
        msg,
        buttons=keyboard,
    )


@bot.on(events.CallbackQuery)
async def handle_action(event: events.CallbackQuery.Event):
    msg, buttons = ActionExecutor(event).execute()
    await bot.send_message(
        event.chat_id,
        msg,
        buttons=buttons,
    )


if __name__ == "__main__":
    setup_db(db)
    bot.start(
        bot_token=os.environ["TG_BOT_TOKEN"],
    )
    bot.run_until_disconnected()
    teardown_db(db)
