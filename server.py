import json

import bottle

import settings
import tasks


@bottle.route('tasks/add/<script>', 'POST')
@bottle.route('tasks/add/<script>:<alias>', 'POST')
def add_task_req(script, alias=None):
    _id = tasks.add_task(script, alias, dict(bottle.request.forms))
    return bottle.HTTPResponse(status=200, body=str(_id))


@bottle.route('tasks/delete/<task_id:int>', 'DELETE')
def delete_task_req(_id):
    tasks.delete_task(_id)


@bottle.route('tasks/get/<task_id:int>', 'GET')
def get_task_req(_id):
    return bottle.HTTPResponse(status=200, body=json.dumps(tasks.get_task(_id)))


@bottle.route('tasks/get', 'GET')
def get_tasks_req():
    return bottle.HTTPResponse(status=200, body=json.dumps(list(tasks.get_task(_id) for _id in tasks.all_tasks)))


bottle.run(host='0.0.0.0', port=8080, debug=settings.ENVIRONMENT == 'dev')

