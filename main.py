import importlib
import sys

import requests.exceptions

import helpers


class TaskException(Exception):
    play = False
    report = True
    reload = False


class SceneErrorException(TaskException):
    play = True


class SceneCriticalErrorException(TaskException):
    pass


class ActionErrorException(TaskException):
    play = True


class ActionCriticalErrorException(TaskException):
    pass


class InvalidConfErrorException(TaskException):
    report = False


class UnknownErrorException(TaskException):
    play = False


class StopException(TaskException):
    play = False
    report = False


class ReloadException(TaskException):
    report = False
    reload = True


def do_task(task, scene, actions, *args, **kwargs):
    scene_inst = scene(*args, **kwargs)
    actions_inst = [action(*args, **kwargs) for action in actions]
    scene_inst.setActionObjects(actions_inst)
    try:
        proxy = helpers.get_proxy(True)
        scene_inst.setProxy(proxy)
        if isinstance(proxy.get('cookies'), dict):
            scene_inst.setCookies(proxy['cookies'])
        if proxy.get('useragent'):
            scene_inst.setUA(proxy['useragent'])
    except (requests.exceptions.RequestException, ConnectionError, TimeoutError):
        pass
    try:
        scene_inst.configure(task)
    except AttributeError:
        pass
    try:
        scene_inst.beginActions()
    except AttributeError:
        pass
    try:
        while True:
            try:
                if not next(scene_inst):
                    break
            except TaskException as e:
                if e.report:
                    requests.patch('http://localhost:8832/tasks/report/' + task['_id'], json={
                        'confirm': True,
                        'stop': (not e.play and not e.reload),
                        'errors': [
                            str(e),
                        ],
                    })
                    if not e.play and e.reload:
                        requests.post('http://localhost:8832/tasks/release/' + task['_id'])
                elif not e.play:
                    if e.reload:
                        requests.post('http://localhost:8832/tasks/release/' + task['_id'])
                    else:
                        requests.post('http://localhost:8832/tasks/finish/' + task['_id'])
    except StopIteration:
        pass
    finally:
        scene_inst.endActions()


def start(service: str, *args, **kwargs):
    try:
        # Import module
        module = importlib.import_module(service)
        # Import scene and actions
        scene = module.scene
        actions = module.actions
        # Import tasks endpoint
        tasks_endpoints = module.tasks_endpoints
        # Wait for tasks
        while True:
            try:
                tasks = requests.get('http://localhost:8832/' + tasks_endpoints).json()
            except (requests.exceptions.RequestException, ConnectionError, TimeoutError):
                continue
            for task in tasks:
                do_task(task, scene, actions, *args, **kwargs)
    except AttributeError:
        print('Fail: service', service, 'configured invalid!')
        raise
    except ImportError:
        print('Fail: service', service, 'not found!')
        raise


def run_exec(executable: str, *args, **kwargs):
    # try to import module and call 'run'
    try:
        module = importlib.import_module(executable)
        return module.run(*args, **kwargs)
    except (ImportError, AttributeError):
        pass
    # try to load module and call method from string (split by '.': now last part is method, other are path to module)
    try:
        exec_parts = executable.split('.')
        return getattr(importlib.import_module('.'.join(exec_parts[:-1])), exec_parts[-1])(*args, **kwargs)
    except ImportError:
        print('Fail: executable', executable, 'not found!')
        raise


if __name__ == '__main__':
    from args_parser import parse_args

    params = parse_args(sys.argv)
    if 'service' in params:
        if not params['service'].endswith('_service'):
            params['service'] += '_service'
        start(**params)
    elif 'exec' in params:
        _exec = params['exec']
        del params['exec']
        run_exec(_exec, **params)
