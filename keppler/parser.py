import os
import json
from datetime import datetime as dt
from typing import Any

from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import peewee as pw

from keppler.models import User, Car, Assurance

load_dotenv()


class Parser:
    MESSAGES_MAP = {
        "user": [
            {
                "role": "system",
                "content": r"Tu es un assitant qui extrait des informations personnelles (nom, prénoms, date de naissance, profession, téléphone, email) \
                        des messages que des clients t\'envoient\ et tu les mets au format json",
            },
            {
                "role": "user",
                "content": "Je m'appelle Jean Dupont, né le 8 Décembre 1966. Je suis ingénieur. Mon téléphone est 0123456789 et mon adresse mail est john@dupont.com",
            },
            {
                "role": "assistant",
                "content": '{"first_name": "Jean", "last_name": "Dupont", "birth_date": "1966-08-12", "profession": "Ingénieur", "phone": "0123456789", "email": "john@dupont.com"}',
            },
            # {
            #     "role": "user",
            #     "content": text,
            # },
        ],
        "car": [],
        "assurance": [],
    }
    MESSAGES_MAP_MOCKED_DATA = {
        "user": {
            "first_name": "Jean",
            "last_name": "Dupont",
            "birth_date": "1966-08-12",
            "profession": "Ingénieur",
            "phone": "0123456789",
            "email": "john@dupont.com",
        },
        "car": {
            "brand": "Renault",
            "model": "Clio",
            "registration_number": "1234567890",
            "year": "2010",
            "energy": "Essence",
            "power": "100",
            "seats": "5",
            "declared_value": 10000,
            "initial_value": 15000,
        },
        "assurance": {
            "start_date": "2024-03-03",
            "end_date": "2024-04-18",
            "registration_number": "CE32829RB",
            "clauses": [1, 3, 6],
        },
    }

    REQUIRED_FIELDS_MAP = {
        "user": [
            "first_name",
            "last_name",
            "birth_date",
            "profession",
        ],
        "car": [
            "brand",
            "model",
            "registration_number",
            "declared_value",
            "initial_value",
        ],
        "assurance": [
            "start_date",
            "end_date",
            "registration_number",
        ],
    }

    def __init__(self):
        self.model = "mistral-small-latest"
        self.client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])
        self.DEBUG = os.environ.get("DEBUG", "1") == "1"

    async def get_model_informations(self, model: str, message: str) -> dict[str, Any]:
        if self.DEBUG:
            return self.MESSAGES_MAP_MOCKED_DATA[model]

        messages = [ChatMessage(**msg) for msg in self.MESSAGES_MAP[model]] + [
            ChatMessage(role="user", content=message)
        ]

        response = self.client.chat(
            model=self.model,
            response_format={"type": "json_object"},
            messages=messages,
        )
        text = response.choices[0].message.content
        return json.loads(text)

    def validate_model_informations(
        self, model: str, data: dict[str, Any]
    ) -> dict[str, Any] | str:
        required_fields = self.REQUIRED_FIELDS_MAP[model]

        for key in required_fields:
            if key not in data:
                return "Veuillez fournir le {missing_key} necéssaires.".format(
                    missing_key=key
                )
        return data

    def create(self, model: str, validated_data: dict[str, Any], **kwargs) -> pw.Model:
        klass: type[pw.Model] = {
            "user": User,
            "car": Car,
            "assurance": Assurance,
        }[model]

        return klass.create(**validated_data, **kwargs)
