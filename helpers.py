import os.path
import re

import colorama
import requests
from urllib3.exceptions import NewConnectionError, MaxRetryError
from requests.exceptions import ConnectionError

DEBUG = True


# Parse raw asins list from TG message or file or other
def get_all_asins_from_text(text: str):
    pattern_find = re.compile('B0[A-Z0-9]{8}')
    asins = set()
    for line in text.strip().splitlines():
        found = pattern_find.findall(line)
        for item in found:
            asins.add(item)
    return list(asins)


def log(*args, **kwargs):
    if DEBUG:
        print(colorama.Back.GREEN, *args, colorama.Back.RESET, **kwargs)
    return True


def parse_args(argv: list[str]):
    params_dict = {}
    for arg in argv:
        row = arg.split('=', 1)
        if len(row) > 1:
            params_dict[row[0]] = row[1]
    return params_dict


def send_bot_msg(user, msg=None, files=None):
    if msg or files:
        try:
            requests.post('http://localhost:8080/send_msg', {'msg': msg, 'uid': user, 'files': files})
        except (ConnectionError, MaxRetryError, ConnectionRefusedError, NewConnectionError):
            pass


def path(*p: str, last_dir=False, filecontent: bool | str = ''):
    curr = ''
    dirs = p if last_dir else p[:-1]
    for item in dirs:
        curr = os.path.join(curr, item)
        if not os.path.exists(curr):
            os.mkdir(curr)
    if not last_dir:
        curr = os.path.join(curr, p[-1])
        if not os.path.exists(curr) and filecontent is not False:
            with open(curr, 'w') as f:
                f.write(filecontent if type(filecontent) is str else '')
    return curr
