from keppler.keyboards import KeyBoard
from keppler.models import Stage, User
from keppler.parser import Parser
from keppler.constants import messages

parser = Parser()


async def process(stage: Stage, message: str) -> tuple[str, KeyBoard | None]:
    if stage.action == "create":
        model = stage.model

        if stage.level == "filling":
            data = await parser.get_model_informations(model=model, message=message)
            validated_data = parser.validate_model_informations(model=model, data=data)

            if isinstance(validated_data, str):
                return validated_data, None

            Stage.update(
                {Stage.data: [validated_data], Stage.level: "request-confirmation"}
            ).where(Stage.user_id == stage.user_id).execute()
            return (
                messages.CREATION_CONFIRMATION_MSG[model].format(**validated_data),
                KeyBoard.CONFIRM,
            )
    return message, get_keyboard(stage.user_id)


def get_keyboard(user_id: int):
    stage = Stage.get_or_none(user_id=user_id)
    if not stage:
        return KeyBoard.UNAUTHENTICATED_USER

    user = User.get(id=user_id)
    if user.cars.count() == 0:
        return KeyBoard.CAR_CREATION

    if user.cars.count() > user.assurances.count():
        return KeyBoard.ASSURANCE_CREATION

    if user.cars.count() == user.assurances.count():
        return KeyBoard.CHECK_ROYALTIES

    return KeyBoard.AUTHENTICATED_USER


def load_fixtures(fixtures: dict):
    for klass, rows in fixtures.items():
        klass.bulk_create([klass(**row) for row in rows])
