import random
import requests

from config import (
    BREVO_API_KEY,
    BREVO_SENDER_EMAIL,
    BREVO_SENDER_NAME
)

OTP_STORAGE = {}


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp(receiver_email):
    otp = generate_otp()

    OTP_STORAGE[receiver_email] = otp

    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {
            "name": BREVO_SENDER_NAME,
            "email": BREVO_SENDER_EMAIL
        },

        "to": [
            {
                "email": receiver_email
            }
        ],

        "subject": "CDMS Login Verification OTP",

        "htmlContent": f"""
        <h2>CDMS Login Verification</h2>

        <p>Your OTP code is:</p>

        <h1>{otp}</h1>

        <p>Do not share this code with anyone.</p>
        """
    }

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10
        )

        print(response.text)

        if response.status_code in [200, 201, 202]:
            return True

        return False

    except Exception as e:
        print("OTP Error:", e)
        return False


def verify_otp(email, user_otp):
    real_otp = OTP_STORAGE.get(email)

    return real_otp == user_otp