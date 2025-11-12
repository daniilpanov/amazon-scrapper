import logging

import requests

from ..helpers import hash_password


class AsinSightRegistrationAPI:
    base_url = "https://api.asinsight.com/v2"
    hub_url = "https://hub.asinsight.com"

    def __init__(self, session: requests.Session, logger: logging.Logger, email: str, nickname: str, password: str):
        self.session = session
        self.logger = logger
        self.email = email
        self.nickname = nickname
        self.password = password

        self.session.headers.update({
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6",
            "dnt": "1",
            "krs-ver": "1.1.0",
            "origin": self.hub_url,
            "referer": f"{self.hub_url}/",
            "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "select-lang": "en-us",
            "content-type": "application/json",
        })

    def check_email_status(self):
        url = f"{self.base_url}/system/register/email/status"
        data = {
            "resource": {},
            "email": self.email,
        }

        response = self.session.post(
            url,
            json=data,
            headers={"request-url": "/sign_up"},
        )

        if response.status_code != 200:
            self.logger.error(f"Error checking email: {response.status_code}")
            return False

        result = response.json()
        self.logger.debug(f"Email status: {result}")
        return result.get("status") == "new"

    def register_email(self):
        return self._send_verification_email()

    def resend_verification_email(self):
        return self._send_verification_email(True)

    def verify_email(self, sign_token):
        response = self.session.post(
            f"{self.base_url}/system/register/email/verify",
            headers={"request-url": "/"},
            json={
                "resource": {},
                "sign": sign_token,
            },
        )

        if response.status_code != 200:
            self.logger.error(f"Verification failed: {response.status_code}")
            return False

        result = response.json()
        self.logger.info("Email verification successful")

        auth_token = result.get("token")
        self.logger.debug(f"AsinSight auth token: {auth_token}")
        return auth_token

    def _send_verification_email(self, is_resend: bool = False):
        url = f"{self.base_url}/system/register/email"
        hashed_password = hash_password(self.password)

        data = {
            "resource": {},
            "nickName": self.nickname,
            "email": self.email,
            "password": hashed_password,
        }

        response = self.session.post(
            url,
            json=data,
            headers={"request-url": "/verify/sign_up/start" if is_resend else "/sign_up"},
        )

        if response.status_code != 200:
            action = "resend" if is_resend else "send"
            self.logger.error(f"Error on {action}: {response.status_code}\nResponse: {response.text}")
            return False

        action = "resend" if is_resend else "send"
        self.logger.debug(f"Verification letter {action}!")
        return True
