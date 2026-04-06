from google.oauth2 import id_token
from google.auth.transport import requests
import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def verify_google_token(token: str) -> dict:
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )
        print("token verified:", idinfo)

        return {
            "user_id": idinfo["sub"],
            "email": idinfo["email"],
            "name": idinfo.get("name", "")
        }

    except Exception as e:
        print("Error verifying Google token:", str(e))
        raise ValueError("Invalid Google token")
