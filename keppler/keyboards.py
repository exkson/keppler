from enum import Enum

from telethon import Button


class KeyBoard(list, Enum):
    CREATE_CAR = [
        Button.inline("📝 Enregistrer une voiture", "create-car"),
    ]
    PAY = [Button.inline("Payer ma redevance", "pay")]
    SUBSRIBE = [Button.inline("Souscrire à une assurance 🚘", "create-assurance")]
    UNAUTHENTICATED_USER = [
        Button.inline("📝 M'enregistrer", "create-user"),
    ]
    CHECK_ROYALTY = [Button.inline("Consulter ma redevance 🔍", "check-royalties")]

    AUTHENTICATED_USER = [
        [*SUBSRIBE, *PAY],
        CREATE_CAR,
    ]
    CAR_CREATION = [
        CREATE_CAR,
        [*SUBSRIBE, *PAY],
    ]

    ASSURANCE_CREATION = [
        SUBSRIBE,
        [
            *PAY,
            *CREATE_CAR,
        ],
    ]
    CHECK_ROYALTIES = [CHECK_ROYALTY, *CAR_CREATION]

    CONFIRM = [
        Button.inline("Confirmer ✅", "confirm"),
        Button.inline("Modifier 🖋️", "modify"),
    ]
