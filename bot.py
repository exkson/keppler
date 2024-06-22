import os
from datetime import date, datetime
import hashlib
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
from keppler.fixtures import FIXTURES
from keppler.utils import process, load_fixtures, get_keyboard
from keppler.command import handle_command
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
    text = event.text

    if text.startswith("/"):
        message = "Commande executée"
        handle_command(text)
        keyboard = get_keyboard(event.sender_id)
    else:
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

        message, keyboard = await process(stage=stage, message=text)

    await bot.send_message(
        event.chat_id,
        message,
        buttons=keyboard,
    )


# Listen buttons events
@bot.on(events.CallbackQuery)
async def action(event: events.CallbackQuery.Event):
    data: str = event.data.decode()
    stage: Stage = Stage.get(user_id=event.sender_id)

    msg = ""
    buttons = None

    if data.startswith("create-"):
        model = data.split("-", 1)[-1]
        Stage.update(
            {Stage.level: "filling", Stage.action: "create", Stage.model: model}
        ).where(Stage.user_id == stage.user_id).execute()
        msg = messages.INFORMATIONS_ASKING_MSG[model].format(
            **(
                {
                    "assurance": {
                        "assurance_choices": Clause.get_choices(),
                    }
                }.get(model, {})
            )
        )
    match data:
        case "check-royalties":
            user: User = User.get(User.id == stage.user_id)
            royalties = user.get_royalties()

            if len(royalties) > 0:
                msg = messages.ROYALTY_CHECK_MSG.format(
                    royalties="----------".join(
                        [
                            """
Voiture : %(car)s
Assurance : %(policy_number)s
Montant : %(amount)s XOF
    """
                            % royalty
                            for royalty in royalties
                        ]
                    )
                )
            else:
                msg = messages.NO_ROYALTIES

            buttons = KeyBoard.CHECK_ROYALTIES

        case "consult-payment-history":
            payments = Payment.select().where(Payment.user_id == stage.user_id)
            if len(payments) == 0:
                msg = messages.NO_PAYMENT_HISTORY_MSG
            else:
                msg = messages.PAYMENT_HISTORY_MSG.format(
                    payments="\n-----------------\n".join(
                        [str(payment) for payment in payments]
                    )
                )
            buttons = get_keyboard(event.sender_id)

        case "confirm":
            model = stage.model

            if stage.action == "create":
                data: dict = stage.data[0]
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

                validated_data = {k: v for k, v in data.items() if v is not None}
                if model == "assurance":
                    validated_data["policy_number"] = hashlib.sha256(
                        datetime.now().isoformat().encode()
                    ).hexdigest()[:8]
                    validated_data["car"] = Car.get(
                        registration_number=data["registration_number"],
                        user_id=event.sender_id,
                    )

                    clauses = validated_data.pop("clauses", [])

                    assurance = klass.create(**validated_data)
                    AssuranceClause.bulk_create(
                        [
                            AssuranceClause(assurance=assurance, clause_id=clause)
                            for clause in clauses
                        ]
                    )
                else:
                    klass.create(**validated_data)

                Stage.update(
                    {
                        Stage.level: None,
                        Stage.action: None,
                        Stage.model: None,
                        Stage.data: [],
                    }
                ).where(Stage.user_id == stage.user_id).execute()

                msg = "Enregistrement effectué avec succès.\n Que désirez-vous faire maintenant ?"
                buttons = get_keyboard(event.sender_id)
        case "modify":
            msg = "Saisissez à nouveau votre message"
            Stage.update({Stage.data: [], Stage.level: "filling"}).where(
                Stage.user_id == stage.user_id
            ).execute()
    await bot.send_message(
        event.chat_id,
        msg,
        buttons=buttons,
    )


if __name__ == "__main__":
    db.create_tables(
        [User, Stage, Payment, Car, Assurance, AssuranceClause, Clause, Document]
    )
    load_fixtures(FIXTURES)

    bot.start(
        bot_token=os.environ["TG_BOT_TOKEN"],
    )
    bot.run_until_disconnected()

    db.drop_tables(
        [User, Stage, Payment, Car, Assurance, AssuranceClause, Clause, Document]
    )
    db.close()
