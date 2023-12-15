import sys
from subprocess import Popen

import state
from telegram_bot2 import log

processes = set()


def add_reviews_tasks(asins):
    good_asins = set()
    for asin in asins:
        if state.get_asin(asin) > -1:
            good_asins.add(asin)
    return add_task('collect_reviews', asins=asins)


def add_products_task(asins, list_name):
    good_asins = set()
    for asin in asins:
        if state.get_asin(asin, 'products') > -1:
            good_asins.add(asin)
    return add_task('collect_products', list_name=list_name, asins=asins)


def add_task(script, *args, stdin=None, stdout=None, stderr=None, **kwargs):
    global processes
    log(f'Process: {script}. Params:', list(kwargs))
    proc = Popen(
        [sys.executable, f'{script}.py', *args, *list(key + '=' + kwargs[key] for key in kwargs)],
        stdin=stdin or sys.stdin, stdout=stdout or sys.stdout, stderr=stderr or sys.stderr,
    )
    log(f'Process [{proc.pid}] started!')
    processes.add(proc)
    new_processes = set()
    for process in processes:
        if process.poll() is None:
            new_processes.add(process)
        else:
            log(f'Process [{process.pid}] exited with code {process.returncode}')
    processes = new_processes
    return proc
