import dataclasses
import logging

import requests

from .register_api import AsinSightRegistrationAPI
from .tempmail_api import TempMailService, TokenSeekStatusEnum

from ..helpers import random_string


class RegistrationException(Exception):
    pass


class NoVerificationTokenException(RegistrationException):
    pass


class VerificationTokenGatheringTimeoutException(RegistrationException):
    pass


class CannotRegisterByThisEmailException(RegistrationException):
    pass


class CannotSendVerificationTokenException(RegistrationException):
    pass


class TempMailException(RegistrationException):
    pass


@dataclasses.dataclass
class AccountInfo:
    nickname: str
    email: str
    password: str
    token: str


def register(session: requests.Session, logger: logging.Logger):
    temp_mail = TempMailService(session, logger)
    if not temp_mail.create_account():
        raise TempMailException()

    test_nickname = random_string()
    test_password = random_string()

    register_controller = AsinSightRegistrationAPI(session, logger, temp_mail.account.email, test_nickname, test_password)

    if not register_controller.check_email_status():
        raise CannotRegisterByThisEmailException()

    if not register_controller.register_email():
        raise CannotSendVerificationTokenException()

    email_generator = temp_mail.wait_for_verification_email()

    for result in email_generator:
        if result[0] == TokenSeekStatusEnum.RESEND:
            if not register_controller.resend_verification_email():
                raise CannotSendVerificationTokenException()

        elif result[0] == TokenSeekStatusEnum.TIMEOUT:
            raise VerificationTokenGatheringTimeoutException()

        elif result[0] == TokenSeekStatusEnum.NO_TOKEN:
            raise NoVerificationTokenException()

        elif result[0] == TokenSeekStatusEnum.READY:
            token = register_controller.verify_email(result[1])
            if not token:
                raise NoVerificationTokenException()

            return AccountInfo(
                nickname=register_controller.nickname,
                email=register_controller.email,
                password=register_controller.password,
                token=token,
            )

    raise RegistrationException("Unknown error")