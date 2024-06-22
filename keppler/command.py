from decimal import Decimal, ConversionSyntax

from keppler.models import Payment, Car, User, Assurance


def handle_command(text: str):
    command, args = text.split(" ", 1)
    if command == "/pay":
        add_payment(args)


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
