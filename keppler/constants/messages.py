from enum import Enum

WELCOME_UNAUTHENTICATED_USER_MSG = (
    "Bienvenue sur notre plateforme, veuillez vous inscrire pour continuer."
)
CREATION_CONFIRMATION_MSG = {
    "user": """Désirez-vous vous inscrire avec les informations suivantes ?
- Nom: {last_name}
- Prénom: {first_name}
- Date de naissance: {birth_date}
- Profession: {profession}
- Téléphone: {phone}
- Email: {email}
""",
    "car": """Désirez-vous vous enregistrer votre voiture avec les informations suivantes ?
- Marque: {brand}
- Modèle: {model}
- Immatriculation: {registration_number}
- Année de mise en circulation: {year}
- Energie: {energy}
- Puissance: {power}
- Nombre de places: {seats}
- Valeur déclarée: {declared_value}
- Valeur d'origine: {initial_value}
    """,
    "assurance": """Désirez-vous souscrire à l'assurance avec les informations suivantes ? :
- Garanties: {clauses}
- Voiture : {registration_number}
- Période: Du {start_date} au {end_date}
- Paiement: Tous les {frequency} mois
""",
}

ASK_USER_CREATION_MSG = """Merci de vous présenter avec vos informations pour que je puisse vous enregistrer.
Exemple: \n
Moi c'est Jean Dupont. Je suis né le 8 Décembre 1966, je suis Ingénieur et mon téléphone est 0123456789. Mon mail est jean@dupont.com"""

ASK_CAR_INFORMATIONS_MSG = """Parlez moi un peu de votre voiture.
J'ai besoin des informations : marque, modèle, immatriculation, valeur déclarée, valeur d'origine, année de mise en circulation, énergie, puissance, nombre de places, ...
"""

ASK_ASSURANCE_INFORMATIONS_MSG = """Pour enregistrer votre assurance, répondez aux questions suivantes : 
- Quel est l'immatriculation de la voiture pour laquelle vous désirez souscrire ?
- Quelles sont les garanties que vous souhaitez souscrire ?
- Quelle période doit couvrir l'assurance ?
- À quelle fréquence désirez-vous payez vos redevances ?
Les garanties que nous offrons sont : 
{clause_choices}

Par exemple, vous pouvez saisir votre réponse sous la forme : 
Je veux les garanties 1, 3, 6 pour la période du 3 Mars 2024 au 18 Avril 2024 et un paiement tous les 6 mois pour la voiture CE32829RB.
"""

ROYALTY_CHECK_MSG = """
Voici les montants de vos redevances pour vos différentes assurances :
{royalties}
"""

PAYMENT_HISTORY_MSG = """
Voici l'historique de vos paiements :
{payments}
"""

NO_PAYMENT_HISTORY_MSG = "Vous n'avez pas encore effectué de paiement."

INFORMATIONS_ASKING_MSG = {
    "user": ASK_USER_CREATION_MSG,
    "car": ASK_CAR_INFORMATIONS_MSG,
    "assurance": ASK_ASSURANCE_INFORMATIONS_MSG,
}

REQUIRES_CAR_TO_SUSCRIBE = (
    "Vous devez d'abord enregistrer une voiture avant de souscrire à une assurance."
)
NO_ROYALTIES = "Vous n'avez pas de redevance à payer."

CREATION_SUCCESS_MSG = "Enregistrement effectué avec succès"

ROYALTY = """
Voiture : %(car)s
Assurance : %(policy_number)s
Montant : %(amount)s XOF
"""

RETYPE_MSG = "Veuillez saisir à nouveau votre message"


class Models(str, Enum):
    USER = "user"
    CAR = "car"
    ASSURANCE = "assurance"
    DOCUMENT = "document"
    CLAUSE = "clause"
    STAGE = "stage"
