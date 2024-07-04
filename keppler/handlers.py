from decimal import Decimal, ConversionSyntax

from keppler.constants import messages
from keppler.models import Payment, Assurance, Stage, User, Clause
from keppler.keyboards import KeyBoard
from keppler.utils import process, get_klass, get_keyboard


async def handle_command(text: str, sender_id: int) -> tuple[str, KeyBoard]:
    command, args = text, None
    if len(command) > 1:
        command, args = text.split(" ", 1)
    msg = ""
    keyboard = None

    # TODO: move logic to class like CommandExecutor
    if command == "/start":
        Stage.create(user_id=sender_id, model="user", action="create", level="new")

        msg = messages.WELCOME_UNAUTHENTICATED_USER_MSG
        keyboard = KeyBoard.UNAUTHENTICATED_USER
    elif command == "/pay":
        add_payment(args)
        msg = "Paiement effectué avec succès"
        keyboard = KeyBoard.CHECK_ROYALTIES
    return msg, keyboard


async def handle_message(text: str, sender_id: int):
    stage, created = Stage.get_or_create(
        user_id=sender_id,
        defaults={"model": "user", "action": "create", "level": "new"},
    )
    msg, keyboard = (
        messages.WELCOME_UNAUTHENTICATED_USER_MSG,
        KeyBoard.UNAUTHENTICATED_USER,
    )

    if not created:
        msg, keyboard = await process(stage=stage, message=text)
    return msg, keyboard


def add_payment(args: str):
    policy_number, amount = args.split(" ", 1)
    if not (
        assurance := Assurance.get_or_none(Assurance.policy_number == policy_number)
    ):
        return

    try:
        amount = Decimal(amount)
    except ConversionSyntax:
        return

    Payment.create(user_id=assurance.user_id, assurance=assurance, amount=amount)


class ActionExecutor:
    def __init__(self, event):
        self.action = event.data.decode()
        self.stage = Stage.get(user_id=event.sender_id)
        self.sender_id = event.sender_id

    def ask_user(self):
        return self._ask_form_filling_for_creation("user")

    def ask_car(self):
        return self._ask_form_filling_for_creation("car")

    def ask_assurance(self):
        msg, keyboard = self._ask_form_filling_for_creation("assurance")
        msg = msg.format(clause_choices=Clause.get_choices())
        return msg, keyboard

    def confirm(self):
        if self.stage.action == "create":
            data: dict = self.stage.data[0]
            klass = get_klass(self.stage.model)

            validated_data = {k: v for k, v in data.items() if v is not None}
            klass.create(**validated_data)

            self.stage.reset()

        return (
            messages.CREATION_SUCCESS_MSG,
            get_keyboard(self.sender_id),
        )

    def modify(self):
        msg = messages.RETYPE_MSG

        self.stage.data = []
        self.stage.level = "filling"
        self.stage.save()

        return msg, None

    def check_royalties(self):
        user = User.get(User.id == self.sender_id)

        if royalties := user.get_royalties():
            msg = messages.ROYALTY_CHECK_MSG.format(
                royalties=("-" * 15).join(
                    [messages.ROYALTY % royalty for royalty in royalties]
                )
            )
        else:
            msg = messages.NO_ROYALTIES

        buttons = KeyBoard.CHECK_ROYALTIES

        return msg, buttons

    def consult_payment_history(self):
        if payments := (Payment.select().where(Payment.user_id == self.sender_id)):
            msg = messages.PAYMENT_HISTORY_MSG.format(
                payments=("-" * 15).join([str(payment) for payment in payments])
            )
        else:
            msg = messages.NO_PAYMENT_HISTORY_MSG

        buttons = get_keyboard(self.sender_id)

        return msg, buttons

    def _ask_form_filling_for_creation(self, model: str) -> tuple[str, None]:
        self.stage.level = "filling"
        self.stage.action = "create"
        self.stage.model = model
        self.stage.save()

        msg = messages.INFORMATIONS_ASKING_MSG[model]

        return msg, None

    def execute(self):
        method = self.action.lower().replace("-", "_")
        if hasattr(self, method):
            return getattr(self, method)()
        return "", None
