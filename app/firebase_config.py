import json
import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore


load_dotenv()


CREDENTIALS_JSON = os.getenv(
    "FIREBASE_CREDENTIALS_JSON",
    ""
).strip()

CREDENTIALS_PATH = os.getenv(
    "FIREBASE_CREDENTIALS_PATH",
    ""
).strip()


if not CREDENTIALS_JSON and not CREDENTIALS_PATH:
    raise RuntimeError(
        "Credenciais do Firebase não configuradas"
    )


if not firebase_admin._apps:

    if CREDENTIALS_JSON:

        try:
            cred_data = json.loads(
                CREDENTIALS_JSON
            )

            cred = credentials.Certificate(
                cred_data
            )

        except json.JSONDecodeError as erro:

            raise RuntimeError(
                "FIREBASE_CREDENTIALS_JSON contém um JSON inválido"
            ) from erro

    else:

        cred = credentials.Certificate(
            CREDENTIALS_PATH
        )

    firebase_admin.initialize_app(
        cred
    )


db = firestore.client()