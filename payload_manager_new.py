import signal
import sys
from subprocess import Popen
from time import sleep

import state
from helpers import log

processes: dict[int, Popen] = {}


def add_reviews_tasks(asins, user_id):
    good_asins = set()
    for asin in asins:
        if state.get_asin(asin) > -1:
            good_asins.add(asin)
    return add_task('collect_reviews', asins=good_asins, user=user_id)


def add_products_task(asins, list_name, user_id):
    good_asins = set()
    for asin in asins:
        if state.get_asin(asin, 'products') > -1:
            good_asins.add(asin)
    return add_task('collect_products', list_name=list_name, asins=good_asins, user=user_id)


def add_task(script, *args, stdin=None, stdout=None, stderr=None, **kwargs):
    log(f'Process: {script}. Params:', list(kwargs))
    proc = Popen(
        [sys.executable, f'{script}.py', *args, *list(key + '=' + kwargs[key] for key in kwargs)],
        stdin=stdin or sys.stdin, stdout=stdout or sys.stdout, stderr=stderr or sys.stderr,
    )
    log(f'Process [{proc.pid}] started!')
    for pid in processes:
        end_task(pid, False)
    processes[proc.pid] = proc
    return proc


def end_task(pid, hard_kill=True):
    global processes
    if pid not in processes:
        raise KeyError

    if hard_kill:
        for sig in [signal.CTRL_C_EVENT, signal.CTRL_BREAK_EVENT, signal.SIGTERM]:
            if processes[pid].poll() is not None:
                break
            processes[pid].send_signal(sig)
            sleep(3)

    if processes[pid].poll() is not None:
        log(f'Process [{pid}] exited with code {processes[pid].returncode}')
        del processes[pid]
