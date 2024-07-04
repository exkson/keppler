from enum import Enum

from telethon import Button


class KeyBoard(list, Enum):
    CREATE_CAR = [Button.inline("Enregistrer une voiture 🚘", "ask-car")]

    SUBSCRIBE = [Button.inline("Souscrire à une assurance 📝", "ask-assurance")]
    UNAUTHENTICATED_USER = [Button.inline(" M'enregistrer ➕", "ask-user")]

    CHECK_ROYALTY = [Button.inline("Consulter ma redevance 🔍", "check-royalties")]
    CONSULT_PAYMENT_HISTORY = [
        Button.inline("Historique des paiements 💳", "consult-payment-history")
    ]

    ASSURANCE_CREATION = [
        SUBSCRIBE,
        CREATE_CAR,
    ]
    CHECK_ROYALTIES = [[*CHECK_ROYALTY, *CONSULT_PAYMENT_HISTORY], *ASSURANCE_CREATION]

    CONFIRM = [
        Button.inline("Confirmer ✅", "confirm"),
        Button.inline("Modifier 🖋️", "modify"),
    ]
