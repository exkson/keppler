import random as rd
from datetime import date
from decimal import Decimal

import peewee as pw
from peewee import fn
from playhouse.sqlite_ext import JSONField

db = pw.SqliteDatabase("keppler.db3")


def current_year():
    return date.today().year


def today():
    return date.today()


class BaseModel(pw.Model):
    class Meta:
        database = db


class User(BaseModel):
    id = pw.BigIntegerField(primary_key=True)
    first_name = pw.CharField(max_length=100)
    last_name = pw.CharField(max_length=100)
    birth_date = pw.DateField()
    phone = pw.CharField(max_length=16, unique=True)
    email = pw.CharField(max_length=100, unique=True)
    gender = pw.CharField(
        max_length=1,
        choices=(
            ("M", "Homme"),
            ("F", "Femme"),
        ),
        default="M",
    )
    profession = pw.CharField(max_length=100, default="")

    address = pw.CharField(max_length=255, default="")
    city = pw.CharField(max_length=100, default="")
    country = pw.CharField(max_length=100, default="")

    def get_royalties(self):
        return [
            {
                "car": assurance.car.registration_number,
                "policy_number": assurance.policy_number,
                "amount": assurance.amount_due,
            }
            for assurance in self.assurances.select().join(Car)
            if assurance.amount_due > 0
        ]


class Document(BaseModel):
    tag = pw.CharField(
        max_length=24,
        choices=(
            ("identity_document", "Pièce d'identité"),
            ("residence_permit", "Carte de séjour"),
            ("passport", "Passeport"),
        ),
    )
    user = pw.ForeignKeyField(User, backref="documents")


class Clause(BaseModel):
    title = pw.CharField(max_length=100)
    description = pw.TextField(default="")
    mandatory = pw.BooleanField(default=False)

    @staticmethod
    def get_choices():
        return "\n".join([f"{clause.id}. {clause.title}" for clause in Clause.select()])


class Car(BaseModel):
    user = pw.ForeignKeyField(User, backref="cars")
    brand = pw.CharField(max_length=100)
    model = pw.CharField(max_length=100)
    registration_number = pw.CharField(max_length=15, unique=True)
    year = pw.IntegerField(default=current_year)
    first_use_date = pw.DateField(default=today)
    usage_type = pw.CharField(
        max_length=3,
        choices=(
            ("P", "Particulier"),
            ("C", "Commercial"),
        ),
        default="P",
    )
    energy = pw.CharField(
        max_length=2,
        choices=(
            ("ES", "Essence"),
            ("GO", "Gasoil"),
            ("EL", "Electrique"),
            ("HY", "Hybride"),
        ),
        default="ES",
    )
    power = pw.IntegerField(default=150)
    seats = pw.IntegerField(default=5)
    declared_value = pw.DecimalField(max_digits=10, decimal_places=2)
    initial_value = pw.DecimalField(max_digits=10, decimal_places=2)


class Assurance(BaseModel):
    user = pw.ForeignKeyField(User, backref="assurances")
    car = pw.ForeignKeyField(Car, backref="assurances")
    start_date = pw.DateField()
    end_date = pw.DateField()
    policy_number = pw.CharField(max_length=100)

    @classmethod
    def create(cls, **query):
        clauses = query.pop("clauses", [])
        assurance = super().create(**query)
        AssuranceClause.bulk_create(
            [
                AssuranceClause(assurance=assurance, clause_id=clause)
                for clause in clauses
            ]
        )
        return assurance

    @property
    def amount(self):
        return sum([clause.monthly_cost for clause in self.clauses]) * (
            Decimal((self.end_date - self.start_date).days / 30)
        )

    @property
    def amount_due(self):
        paid = Decimal(
            (
                Payment.select(fn.SUM(Payment.amount))
                .where(Payment.assurance == self)
                .scalar()
            )
            or 0
        )
        return round(self.amount - paid, 2)


def get_monthly_cost():
    return round(Decimal(rd.random() * 1e5), 2)


class AssuranceClause(BaseModel):
    assurance = pw.ForeignKeyField(Assurance, backref="clauses")
    clause = pw.ForeignKeyField(Clause, backref="assurances")
    monthly_cost = pw.DecimalField(
        max_digits=10, decimal_places=2, default=get_monthly_cost
    )


class Payment(BaseModel):
    user = pw.ForeignKeyField(User, backref="payments")
    assurance = pw.ForeignKeyField(Assurance, backref="payments")
    amount = pw.DecimalField(max_digits=10, decimal_places=2)
    date = pw.DateField(default=date.today)

    def __str__(self) -> str:
        return """Date: {date}
Montant: {amount}
Assurance : {assurance}""".format(
            date=self.date.strftime("%d/%m/%Y"),
            amount=self.amount,
            assurance=self.assurance.policy_number,
        )


class Stage(BaseModel):
    user_id = pw.CharField(max_length=16, primary_key=True)
    model = pw.CharField(
        max_length=24,
        choices=(
            ("user", "Utilisateur"),
            ("car", "Voiture"),
            ("assurance", "Assurance"),
            ("document", "Document"),
            ("clause", "Clause"),
        ),
        null=True,
    )
    action = pw.CharField(
        max_length=10,
        choices=(
            ("create", "Créer"),
            ("update", "Mettre à jour"),
            ("delete", "Supprimer"),
        ),
        null=True,
    )
    level = pw.CharField(max_length=24, null=True)
    data = JSONField(default=[])

    def reset(self):
        self.model = None
        self.action = None
        self.level = None
        self.data = []
        self.save()
