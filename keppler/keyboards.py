from enum import Enum

from telethon import Button


class KeyBoard(list, Enum):
    AUTHENTICATED_USER = [
        [
            Button.inline("Souscrire à une assurance 🚘", "subscribe"),
            Button.inline("Payer ma redevance", "pay"),
        ],
        [
            # Button.inline("Consulter la FAQ 📚", "faq"),
            # Button.inline("Prendre rendez-vous 📞", "contact"),
            Button.inline("📝 Enrégistrer une voiture", "declare-car"),
        ],
    ]
    CAR_CREATION = [
        [Button.inline("Enregistrer une voiture 🚘", "declare-car")],
        [
            Button.inline("Souscrire à une assurance 📄", "subscribe"),
            Button.inline("Payer ma redevance 💰", "pay"),
        ],
    ]

    ASSURANCE_CREATION = [
        [
            Button.inline("Souscrire à une assurance 📄", "subscribe"),
        ],
        [
            Button.inline("Payer ma redevance 💰", "pay"),
            Button.inline("Enregistrer une voiture 🚘", "declare-car"),
        ],
    ]
    UNAUTHENTICATED_USER = [
        Button.inline("📝 M'enregistrer", "register"),
    ]

    CONFIRM = [
        Button.inline("Confirmer ✅", "confirm"),
        Button.inline("Modifier 🖋️", "modify"),
    ]
