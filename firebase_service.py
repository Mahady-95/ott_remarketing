# import firebase_admin
# from firebase_admin import credentials, messaging

# cred = credentials.Certificate("firebase_key.json")

# if not firebase_admin._apps:
#     firebase_admin.initialize_app(cred)

# def send_push_notification(device_token: str, title: str, body: str):
#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=title,
#             body=body
#         ),
#         token=device_token
#     )

#     response = messaging.send(message)
#     return response


import os
import firebase_admin

from dotenv import load_dotenv
from firebase_admin import credentials, messaging

load_dotenv()

cred = credentials.Certificate(
    os.getenv("FIREBASE_CREDENTIALS")
)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)


def send_push_notification(device_token: str, title: str, body: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=device_token
    )

    response = messaging.send(message)

    return response