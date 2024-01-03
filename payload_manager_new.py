import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from subprocess import Popen
from time import sleep

import state
from helpers import log

processes: dict[int, Popen] = {}
i = 0
processes_waiters = ThreadPoolExecutor(3)


def add_reviews_tasks(asins, user_id):
    for asin in asins:
        processes_waiters.submit(add_task, 'collect_reviews', asin=asin, user=str(user_id))


def add_products_task(asins, list_name, user_id):
    good_asins = set()
    for asin in asins:
        if state.get_asin(asin, 'products') > -1:
            good_asins.add(asin)
    processes_waiters.submit(add_task, 'collect_products', list_name=list_name, asins=''.join(good_asins), user=str(user_id))


def add_deals_task(name, user_id):
    processes_waiters.submit(add_task, 'collect_all_deals', sheet_name=name, user=user_id)


def add_asins_nearby_task(asin, user_id):
    processes_waiters.submit(add_task, 'collect_asins_nearby', asin=asin, user=user_id)


def add_departments_task(department, user_id):
    processes_waiters.submit(add_task, 'collect_departments', dep_name=department, user=user_id)


# Добавление процесса и ожидание завершения (ф-я запускается в отдельном потоке)
def add_task(script, *args, stdin=None, stdout=None, stderr=None, **kwargs):
    global i
    log(f'Process: {script}. Params:', dict(kwargs))
    kwargs['_id'] = i
    proc = Popen(
        [sys.executable, f'{script}.py', *args, *list(key + '=' + str(kwargs[key]) for key in kwargs)],
        stdin=stdin or sys.stdin, stdout=stdout or sys.stdout, stderr=stderr or sys.stderr,
    )
    log(f'Process [{kwargs["_id"]}] started!')
    for _id in processes:
        end_task(_id, False)
    processes[kwargs['_id']] = proc
    # Ожидание завершения процесса
    proc.wait()
    if i not in processes and i > 255:
        i = 0
    else:
        i += 1


def end_task(_id, hard_kill=True):
    global processes
    _id = int(_id)
    if _id not in processes:
        raise KeyError

    if hard_kill and processes[_id].poll() is None:
        processes[_id].send_signal(signal.SIGTERM)
        sleep(3)

    if processes[_id].poll() is not None:
        log(f'Process [{_id}] exited with code {processes[_id].returncode}')
        del processes[_id]
