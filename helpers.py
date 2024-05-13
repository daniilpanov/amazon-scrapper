import asyncio
import os.path
import re
from functools import wraps, partial
from time import sleep

from more_itertools import batched

import colorama
import requests
from urllib3.exceptions import NewConnectionError, MaxRetryError
from requests.exceptions import ConnectionError

import tasks_manager

DEBUG = True


def to_async(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


def get_proxies_list():
    r = requests.get(
        'https://proxy.webshare.io/api/v2/proxy/list/download/fylqlgwtujdvttnfaorztplrphexumivqxzmwiof/-/any/username/direct/-/')
    if r.status_code == 200:
        res = []
        for i in r.text.splitlines():
            res.append(i.split(':'))
        return res
    sleep(10)
    return get_proxies_list()


def chunk_asins(asins_raw):
    return list(''.join(i) for i in batched(asins_raw, 10))


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
        except (ConnectionError, MaxRetryError, ConnectionRefusedError, ConnectionResetError, NewConnectionError):
            pass


def captcha_solve(url):
    try:
        result = requests.post('http://localhost:8090/solve/url', json={'url': url}, headers={'Content-Type': 'application/json'})
    except (ConnectionError, MaxRetryError, ConnectionRefusedError, ConnectionResetError, NewConnectionError):
        return None
    if result.status_code == 200:
        return result.content.decode('utf-8')
    return None


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


def get_task_loop(func, script, delay=5000, ev=None, *, pre_func=None, post_func=None):
    task = None
    if pre_func:
        pre_func()
    try:
        while not ev or not ev.is_set():
            task = tasks_manager.get_one_task({
                'script': script,
                'taskLock': {'$exists': False},
                'status': {'$lte': tasks_manager.TaskStatusEnum.started},
                '$expr': {'$eq': ['$status', '$confirmed_status']},
            })
            if task:
                # Если не получается захватить задачу -- пропускаем
                if not tasks_manager.acquire_task(script, task['_id'], task['taskHeader']['_id']):
                    task = None
                    continue
                # Если захватили -- запускаем функцию
                try:
                    func(task)
                # Ошибки логируем
                except Exception:
                    # TODO: log
                    pass
                # Отпускаем задачу
                tasks_manager.release_task(task['_id'])
                task = None
            sleep(delay / 1000)
    except KeyboardInterrupt:
        if post_func:
            post_func(task)
        raise
