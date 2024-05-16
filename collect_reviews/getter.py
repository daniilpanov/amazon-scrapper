from time import sleep

import tasks
from tasks import TaskStatusEnum
from .collect import collect


def start():
    while True:
        sleep(1)
        task = tasks.get_one_task('reviews', with_status=[TaskStatusEnum.created, TaskStatusEnum.started], locked=False)
        if not task or not tasks.acquire_task(task['_id']):
            continue
        _id = task['_id']
        params = task.get('params')
        if not params:
            tasks.delete_task(task['_id'])
            continue
        asin = params.get('asin')
        if not asin:
            tasks.delete_task(task['_id'])
            continue
        keywords = params.get('keywords', '')
        domain = params.get('domain', 'amazon.com')
        params_seed = task.get('hidden', {}).get('params_seed', 0)
        curr_format = params.get('current_format', True)

        tasks.confirm_task(_id, task.get('status', 1), True, 'started_at')
        try:
            collect(_id, asin, keywords, domain, params_seed, curr_format)
        except Exception as e:
            tasks.report_error(_id, ('critical', type(e).__name__, str(e)))
        tasks.release_task(_id)
        tasks.confirm_task(_id, tasks.TaskStatusEnum.finished, True, 'ended_at')
