import os
from datetime import date
import logging

import dotenv
from telethon import TelegramClient, events
import peewee as pw

dotenv.load_dotenv()

from keppler.models import (
    User,
    Stage,
    Payment,
    Car,
    Assurance,
    AssuranceClause,
    Clause,
    Document,
    db,
)
from keppler.utils import process
from keppler.constants import messages

from keppler.keyboards import KeyBoard

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
async def incoming_message(event: events.NewMessage.Event):
    stage, created = Stage.get_or_create(
        user_id=event.sender_id,
        defaults={"model": "user", "action": "create", "level": "new"},
    )
    if created:
        await bot.send_message(
            event.chat_id,
            messages.WELCOME_UNAUTHENTICATED_USER_MSG,
            buttons=KeyBoard.UNAUTHENTICATED_USER,
        )
        return

    message, keyboard = await process(stage=stage, message=event.text)

    await bot.send_message(
        event.chat_id,
        message,
        buttons=keyboard,
    )


@bot.on(events.CallbackQuery)
async def action(event: events.CallbackQuery.Event):
    data = event.data.decode()
    stage: Stage = Stage.get(user_id=event.sender_id)

    msg = ""
    buttons = None

    match data:
        case "register":
            # Register as new user
            Stage.update({Stage.level: "filling"}).where(
                Stage.user_id == stage.user_id
            ).execute()
            msg = messages.ASK_USER_CREATION_MSG
        case "declare-car":
            # Declare a new car
            Stage.update(
                {Stage.level: "filling", Stage.action: "create", Stage.model: "car"}
            ).where(Stage.user_id == stage.user_id).execute()
            msg = messages.ASK_CAR_INFORMATIONS_MSG
        case "subscribe":
            # Subscribe to an assurance
            Stage.update(
                {
                    Stage.level: "filling",
                    Stage.action: "create",
                    Stage.model: "assurance",
                }
            ).where(Stage.user_id == stage.user_id).execute()
            msg = messages.ASK_ASSURANCE_INFORMATIONS_MSG
        case "confirm":
            model = stage.model

            if stage.action == "create":
                data = stage.data[0]
                klass: type[pw.Model] = {
                    "user": User,
                    "car": Car,
                    "assurance": Assurance,
                    "document": Document,
                    "clause": Clause,
                }[model]

                if model == "user":
                    data["id"] = event.sender_id
                else:
                    data["user_id"] = event.sender_id
                if model == "assurance":
                    data["start_date"] = date.today()
                    data["end_date"] = date.today()
                    data["policy_number"] = "123456789"
                    data["car"] = Car.get(
                        registration_number=data["registration_number"],
                        user_id=event.sender_id,
                    )

                    clauses = data.pop("clauses", [])

                    assurance = klass.create(**data)
                    AssuranceClause.bulk_create(
                        [
                            AssuranceClause(assurance=assurance, clause_id=clause)
                            for clause in clauses
                        ]
                    )
                else:
                    klass.create(**data)

                Stage.update(
                    {
                        Stage.level: None,
                        Stage.action: None,
                        Stage.model: None,
                        Stage.data: [],
                    }
                ).where(Stage.user_id == stage.user_id).execute()

                msg = "Enregistrement effectué avec succès.\n Que désiez-vous faire maintenant ?"
                buttons = KeyBoard.AUTHENTICATED_USER

    await bot.send_message(
        event.chat_id,
        msg,
        buttons=buttons,
    )


if __name__ == "__main__":
    db.create_tables(
        [User, Stage, Payment, Car, Assurance, AssuranceClause, Clause, Document]
    )
    bot.start(
        bot_token=os.environ["TG_BOT_TOKEN"],
    )
    bot.run_until_disconnected()
    db.drop_tables(
        [User, Stage, Payment, Car, Assurance, AssuranceClause, Clause, Document]
    )
    db.close()
