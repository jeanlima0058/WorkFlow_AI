import os
import json

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")
CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")


if not CREDENTIALS_JSON and not CREDENTIALS_PATH:
    raise RuntimeError(
        "Credenciais do Firebase não configuradas"
    )


if not firebase_admin._apps:

    if CREDENTIALS_JSON:
        # Utilizado no Render
        cred = credentials.Certificate(
            json.loads(CREDENTIALS_JSON)
        )

    else:
        # Utilizado localmente
        cred = credentials.Certificate(
            CREDENTIALS_PATH
        )

    firebase_admin.initialize_app(cred)


db = firestore.client()