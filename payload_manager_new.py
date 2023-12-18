import signal
import sys
from subprocess import Popen
from time import sleep

import state
from helpers import log

processes: dict[int, Popen] = {}


def add_reviews_tasks(asins, user_id):
    tasks = []
    for asin in asins:
        tasks.append(add_task('collect_reviews', asin=asin, user=str(user_id)))
    return tasks


def add_products_task(asins, list_name, user_id):
    return
    good_asins = set()
    for asin in asins:
        if state.get_asin(asin, 'products') > -1:
            good_asins.add(asin)
    return add_task('collect_products', list_name=list_name, asins=''.join(good_asins), user=str(user_id))


def add_task(script, *args, stdin=None, stdout=None, stderr=None, **kwargs):
    log(f'Process: {script}. Params:', list(kwargs))
    kwargs['_id'] = str(len(processes))
    proc = Popen(
        [sys.executable, f'{script}.py', *args, *list(key + '=' + kwargs[key] for key in kwargs)],
        stdin=stdin or sys.stdin, stdout=stdout or sys.stdout, stderr=stderr or sys.stderr,
    )
    log(f'Process [{kwargs["_id"]}] started!')
    for _id in processes:
        end_task(_id, False)
    processes[kwargs['_id']] = proc
    return proc


def end_task(_id, hard_kill=True):
    global processes
    if _id not in processes:
        raise KeyError

    if hard_kill:
        for sig in [signal.CTRL_C_EVENT, signal.CTRL_BREAK_EVENT, signal.SIGTERM]:
            if processes[_id].poll() is not None:
                break
            processes[_id].send_signal(sig)
            sleep(3)

    if processes[_id].poll() is not None:
        log(f'Process [{_id}] exited with code {processes[_id].returncode}')
        del processes[_id]
