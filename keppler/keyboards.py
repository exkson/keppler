from enum import Enum

from telethon import Button


class KeyBoard(list, Enum):
    CREATE_CAR = [Button.inline("Enregistrer une voiture 🚘", "create-car")]

    SUBSRIBE = [Button.inline("Souscrire à une assurance 📝", "create-assurance")]
    UNAUTHENTICATED_USER = [Button.inline(" M'enregistrer ➕", "create-user")]

    CHECK_ROYALTY = [Button.inline("Consulter ma redevance 🔍", "check-royalties")]
    CONSULT_PAYMENT_HISTORY = [
        Button.inline("Historique des paiements 💳", "consult-payment-history")
    ]

    ASSURANCE_CREATION = [
        SUBSRIBE,
        CREATE_CAR,
    ]
    CHECK_ROYALTIES = [[*CHECK_ROYALTY, *CONSULT_PAYMENT_HISTORY], *ASSURANCE_CREATION]

    CONFIRM = [
        Button.inline("Confirmer ✅", "confirm"),
        Button.inline("Modifier 🖋️", "modify"),
    ]
