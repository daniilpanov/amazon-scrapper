import hashlib
import random
import string


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def hash_password(password):
    return hashlib.sha1(password.encode()).hexdigest()
