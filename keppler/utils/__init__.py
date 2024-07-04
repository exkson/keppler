import peewee as pw

from keppler.keyboards import KeyBoard
from keppler.models import (
    Stage,
    User,
    Payment,
    Car,
    Assurance,
    AssuranceClause,
    Clause,
    Document,
)
from keppler.fixtures import FIXTURES
from keppler.parser import Parser
from keppler.constants import messages


async def process(stage: Stage, message: str) -> tuple[str, KeyBoard | None]:
    if stage.action == "create":
        model = stage.model

        if stage.level == "filling":
            parser = Parser(stage.user_id)

            data = await parser.get_model_informations(model=model, message=message)
            validated_data = parser.validate_model_informations(model=model, data=data)

            if isinstance(validated_data, str):
                return validated_data, None

            Stage.update(
                {Stage.data: [validated_data], Stage.level: "request-confirmation"}
            ).where(Stage.user_id == stage.user_id).execute()

            return (
                messages.CREATION_CONFIRMATION_MSG[model].format(
                    **{key: value or "inconnu" for key, value in validated_data.items()}
                ),
                KeyBoard.CONFIRM,
            )

    if User.get_or_none(id=stage.user_id) is None:
        return messages.WELCOME_UNAUTHENTICATED_USER_MSG, KeyBoard.UNAUTHENTICATED_USER
    return message, get_keyboard(stage.user_id)


def get_keyboard(user_id: int):
    stage = Stage.get_or_none(user_id=user_id)
    if not stage or User.get_or_none(id=user_id) is None:
        return KeyBoard.UNAUTHENTICATED_USER

    user = User.get(id=user_id)
    if user.cars.count() == 0:
        return KeyBoard.CREATE_CAR

    return KeyBoard.CHECK_ROYALTIES


def load_fixtures(fixtures: dict):
    for klass, rows in fixtures.items():
        klass.bulk_create([klass(**row) for row in rows])


def setup_db(db):
    db.create_tables(
        [User, Stage, Payment, Car, Assurance, AssuranceClause, Clause, Document]
    )
    load_fixtures(FIXTURES)


def teardown_db(db):
    db.drop_tables(
        [User, Stage, Payment, Car, Assurance, AssuranceClause, Clause, Document]
    )
    db.close()


def get_klass(model: str) -> type[pw.Model]:
    return {
        "user": User,
        "car": Car,
        "assurance": Assurance,
        "document": Document,
        "clause": Clause,
    }[model]
