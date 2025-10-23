import dataclasses
import enum
import logging
import random
import time

import requests

from ..helpers import random_string


class TokenSeekStatusEnum(enum.Enum):
    RESEND = 0
    NO_TOKEN = 1
    TIMEOUT = 2
    READY = 3


@dataclasses.dataclass
class TempMailAccount:
    email: str
    password: str


class TempMailService:
    account: TempMailAccount | None = None

    def __init__(self, session: requests.Session, logger: logging.Logger):
        self.session = session
        self.logger = logger

    def get_available_domains(self):
        try:
            response = self.session.get("https://api.mail.tm/domains")
            if response.status_code == 200:
                domains = response.json()["hydra:member"]
                return [domain["domain"] for domain in domains]
        except:
            pass

        return ["gmail.com", "yahoo.com", "hotmail.com"]

    def create_account(self):
        domains = self.get_available_domains()
        domain = random.choice(domains)

        self.account = TempMailAccount(
            email=f"{random_string()}@{domain}",
            password=random_string(),
        )

        try:
            response = self.session.post("https://api.mail.tm/accounts", json={
                "address": self.account.email,
                "password": self.account.password,
            })

            if response.status_code not in [200, 201]:
                self.logger.error(f"Can not create temp mail: {response.status_code}")
                return False

            self.logger.info(f"Temp mail created: {self.account.email}")

            token_response = self.session.post("https://api.mail.tm/token", json={
                "address": self.account.email,
                "password": self.account.password,
            })
            if token_response.status_code != 200:
                return False

            token = token_response.json()["token"]
            self.session.headers["Authorization"] = f"Bearer {token}"
            return True

        except Exception as e:
            self.logger.exception(f"Can not create temp mail: {e}")

        return False

    def get_messages(self):
        try:
            messages_response = self.session.get("https://api.mail.tm/messages")
            if messages_response.status_code == 200:
                return messages_response.json()["hydra:member"]

        except Exception as e:
            self.logger.exception(f"Error on trying to handle a message: {e}")

        return []

    def wait_for_verification_email(self, timeout=120, check_interval=5):
        self.logger.debug("Wait for verification email...")

        start_time = time.time()
        last_resend_time = start_time
        resend_interval = 20

        while time.time() - start_time < timeout:
            current_time = time.time()
            if current_time - last_resend_time >= resend_interval:
                self.logger.debug("Resend the message...")
                yield (TokenSeekStatusEnum.RESEND,)
                last_resend_time = current_time

            messages = self.get_messages()

            for message in messages:
                if "asinsight" in message.get("from", {}).get("address", "").lower():
                    token = self.extract_verification_token(message["id"])
                    self.logger.info(f"Verification is found! Token: {token}")

                    if token:
                        yield TokenSeekStatusEnum.READY, token
                        return

                    yield (TokenSeekStatusEnum.NO_TOKEN,)

            self.logger.debug(f"Retry after {check_interval}s")
            time.sleep(check_interval)

        self.logger.error("Message waiting timeout error")
        yield (TokenSeekStatusEnum.TIMEOUT,)

    def extract_verification_token(self, message_id) -> str | None:
        try:
            message_response = self.session.get(f"https://api.mail.tm/messages/{message_id}")
            if message_response.status_code != 200:
                self.logger.error("Can not get message!")
                return None

            message_data = message_response.json()
            text = message_data.get("text", "")

            import re
            sign_match = re.search(r"sign=([a-f0-9]+)", text)
            if sign_match:
                return sign_match.group(1)
        except Exception as e:
            self.logger.exception(f"Error on token extracting: {e}")
