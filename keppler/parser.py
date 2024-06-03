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
            {
                "role": "user",
                "content": "Je m'appelle Mamane Traoré, mamane@gmail.com",
            },
            {
                "role": "assistant",
                "content": '{"first_name": "Mamane", "last_name": "Traoré", "birth_date": null, "profession": null, "phone": null, "email": "mamane@gmail.com"}',
            },
            {
                "role": "user",
                "content": "Mamadou Doucouré 12/12/1980 Chauffeur 65879934 mdoucoure@yahoo.com",
            },
            {
                "role": "assistant",
                "content": '{"first_name": "Mamadou", "last_name": "Doucouré", "birth_date": "1980-12-12, "profession": "Chauffeur, "phone": "65879934", "email": "mdoucoure@yahoo.com"}',
            },
        ],
        "car": [
            {
                "role": "system",
                "content": r"Tu es un assitant qui extrait des informations sur une voiture (marque, modèle, numéro d'immatriculation, année, énergie, puissance, nombre de places, valeur déclarée, valeur initiale) \
                        des messages que des clients t'envoient\ et tu les mets au format json",
            },
            {
                "role": "user",
                "content": "Je possède une Renault Clio immatriculée BB4567RB de l'année 2010. C'est une voiture essence de 100 chevaux avec 5 places acheté à 15000 qui vaut maintenant 10000.",
            },
            {
                "role": "assistant",
                "content": '{"brand": "Renault", "model": "Clio", "registration_number": "BB4567RB", "year": "2010", "energy": "Essence", "power": "100", "seats": "5", "declared_value": 10000, "initial_value": 15000}',
            },
            {
                "role": "user",
                "content": "Je possède une Peugeot 508 de l'année 2015, immatriculée CA9921RB, essence, 120 chevaux, 5 places.",
            },
            {
                "role": "assistant",
                "content": '{"brand": "Peugeot", "model": "508", "registration_number": "CA9921RB", "year": "2015", "energy": "Essence", "power": "120", "seats": "5", "declared_value": null, "initial_value": null}',
            },
        ],
        "assurance": [
            {
                "role": "system",
                "content": r"Tu es un assitant qui extrait des informations sur une assurance (date de début, date de fin, numéro d'immatriculation, clauses) \
                        des messages que des clients t'envoient\ et tu les mets au format json",
            },
            {
                "role": "user",
                "content": "Je veux assurer ma voiture immatriculée CE32829RB du 3 Mars 2024 au 18 Avril 2024 avec les garanties 1, 3, 6.",
            },
            {
                "role": "assistant",
                "content": '{"start_date": "2024-03-03", "end_date": "2024-04-18", "registration_number": "CE32829RB", "clauses": [1, 3, 6]}',
            },
            {
                "role": "user",
                "content": "CA9921RB du 22 Janvier 2023 au 25 Avril 2024 avec les garanties 4, 2.",
            },
            {
                "role": "assistant",
                "content": '{"start_date": "2023-01-22", "end_date": "2024-04-25", "registration_number": "CA9921RB", "clauses": [4, 2]}',
            },
        ],
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
            "registration_number": "CE32829RB",
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
            "frequency": 3,
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
            "frequency",
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
