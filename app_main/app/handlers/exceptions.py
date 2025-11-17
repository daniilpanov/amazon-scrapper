class HandlerException(Exception):
    pass


class InvalidDataException(HandlerException):
    pass


class NotFoundException(HandlerException):
    pass
