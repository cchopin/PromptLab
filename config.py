# Configuration centrale de PromptLab.
# Contient les parametres de base de donnees et les valeurs par defaut.

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Chemin de la base SQLite (fichier local dans le repertoire du projet)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "promptlab.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cle de session Flask (outil local, valeur simple suffisante)
    SECRET_KEY = os.environ.get("PROMPTLAB_SECRET", "promptlab-local-dev")

    # Timeout par defaut des requetes vers les cibles LLM (secondes)
    DEFAULT_TIMEOUT = int(os.environ.get("PROMPTLAB_TIMEOUT", "60"))

    # Delai maximum autorise entre deux steps d'une chaine (securite, ms)
    MAX_CHAIN_DELAY_MS = 10000
