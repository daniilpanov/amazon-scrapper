import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen
from time import sleep

import state
from helpers import log

processes: dict[int, Popen] = {}
processes_waiters = ThreadPoolExecutor(os.cpu_count())
alive = True


def add_reviews_tasks(asins, user_id, callback=None, domain=None, current_format=True):
    for asin in asins:
        processes_waiters.submit(
            add_task, 'collect_reviews', asin=asin,
            user=str(user_id), callback=callback, domain=domain,
            current_format=current_format,
        )


def add_products_task(asins, list_name, user_id, callback=None, domain=None):
    # good_asins = set()
    # for asin in asins:
    #     if state.get_asin(asin, 'products') > -1:
    #         good_asins.add(asin)
    good_asins = set(asins)
    processes_waiters.submit(
        add_task, 'collect_products', list_name=list_name or '',
        asins=''.join(good_asins), user=str(user_id), callback=callback, domain=domain,
    )


def add_amazon_aspects_task(name, asins, user_id, domain):
    processes_waiters.submit(
        add_task, 'collect_amazon_aspects', list_name=name,
        asins=''.join(asins), user=user_id, domain=domain,
    )


def add_asins_nearby_task(asin, user_id, limit, domain):
    processes_waiters.submit(add_task, 'collect_asins_nearby', asin=asin, user=user_id, limit=limit, domain=domain)


def add_departments_task(department, user_id, domain):
    processes_waiters.submit(add_task, 'collect_departments', dep_name=department, user=user_id, domain=domain)


# Добавление процесса и ожидание завершения (ф-я запускается в отдельном потоке)
def add_task(script, *args, stdin=None, stdout=None, stderr=None, **kwargs):
    if not alive:
        return
    log(f'Process: {script}. Params:', dict(kwargs))
    _id = hash(hash(str(args)) + hash(str(kwargs)) + hash(script))
    while _id in processes:
        _id += 1
    kwargs['_id'] = _id
    proc = Popen(
        [sys.executable, f'{script}.py', *args, *list(key + '=' + str(kwargs[key]) for key in kwargs)],
        stdin=stdin or sys.stdin, stdout=stdout or sys.stdout, stderr=stderr or sys.stderr,
    )
    log(f'Process [{_id}] started!')
    for item_id in processes:
        end_task(item_id, False, False)
    processes[_id] = proc
    # Ожидание завершения процесса
    proc.wait()
    if 'callback' in kwargs:
        kwargs['callback']()


def end_task(_id, hard_kill=True, exc=True):
    global processes
    _id = int(_id)
    if _id not in processes:
        if exc:
            raise KeyError
        return False

    if hard_kill and processes[_id].poll() is None:
        processes[_id].send_signal(signal.SIGTERM)
        sleep(3)

    if processes[_id].poll() is not None:
        log(f'Process [{_id}] exited with code {processes[_id].returncode}')
        del processes[_id]
        return True
    return False
