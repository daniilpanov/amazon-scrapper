import importlib
import random
import sys
import requests.exceptions
import time
import PyQt5.QtWebEngineWidgets
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtWidgets import QApplication

from exceptions import *


class Starter:

    # Yes, it is antipattern, but it is very compact
    def __init__(self, service: str, *args, **kwargs):
        self.service = service
        # Create an app
        app = QApplication([])
        try:
            # Import module
            module = importlib.reload(importlib.import_module(service))  # raise_2
            # Import scene and actions; create scene
            self.scene = module.scene(*args, **kwargs)  # raise_1
            self.actions = module.actions  # raise_1
            # Import tasks endpoint
            self.endpoints = module.tasks_endpoints  # raise_1
            # Connect events
            self.scene.success_signal.connect(self.success)
            self.scene.set_stage_signal.connect(self.set_stage)
            self.scene.set_stage_res_signal.connect(self.set_stage)
            self.scene.set_stage_res_key_signal.connect(self.set_stage)
            self.scene.report_signal.connect(self.report)
            self.scene.reload_signal.connect(self.reload)
            self.scene.proxy_change_signal.connect(self.proxyChange)
            # Setup actions
            actions_inst = [action(self.scene) for action in self.actions]
            self.scene.setActionObjects(actions_inst)
            # Low down server payload
            time.sleep(5)
            print('iter!')
            self.next_task()
            app.exec_()
        except AttributeError:  # MARK: raise_1
            print('Fail: service', service, 'configured invalid!')
            raise
        except ImportError:  # MARK: raise_2
            print('Fail: service', service, 'not found!')
            raise
        finally:
            QApplication.quit()

    def success(self, task_id: str):
        self.scene.endScene()
        requests.patch('http://localhost:8832/tasks/finish/' + task_id)
        self.reload(task_id)
        return self.next_task()

    def set_stage(self, task_id: str, stage: int, res: object | None = None, key: str | None = None):
        self.scene.endScene()
        requests.patch('http://localhost:8832/tasks/stage/' + task_id, json={
            'release': True,
            'stage': stage,
            'result': res,
            'result_key': key,
        })
        return self.next_task()

    def report(self, task_id: str, error: str, play: bool, reload: bool):
        requests.patch('http://localhost:8832/tasks/report/' + task_id, json={
            'confirm': True,
            'stop': (not play and not reload),
            'errors': [error],
        })
        if not play and reload:
            self.reload(task_id)

    def reload(self, task_id):
        requests.post('http://localhost:8832/tasks/release/' + task_id)

    def proxyChange(self, task_id):
        if self.scene.need_proxy:
            proxy_conf = requests.get('http://localhost:8833/proxy/random')
            if proxy_conf.status_code == 200:
                proxy_conf = proxy_conf.json()
                if 'details' not in proxy_conf:
                    print(proxy_conf)
                    del proxy_conf['cookies']
                    del proxy_conf['useragent']
                    self.scene.setGlobalProxy(proxy_conf['addr'], proxy_conf['port'], proxy_conf['username'], proxy_conf['password'])
            return self.reload(task_id)
        return self.report(task_id, 'Connection error!', False, False)

    def next_task(self):
        # Get tasks and do it
        tasks = []
        while not tasks:
            try:
                for endpoint in self.endpoints:
                    tasks.extend(requests.get('http://localhost:8832/' + endpoint).json())
                time.sleep(5)
            except (requests.exceptions.RequestException, ConnectionError, TimeoutError) as e:
                print(e)
                pass
            print('got tasks:', tasks)
        self.do_task(random.choice(tasks))

    def do_task(self, task):
        `res = requests.post('http://localhost:8832/tasks/acquire/' + task['script'] + '/' + task['header_id'] + '/' + task['_id'])
        if res.status_code == 409:
            return self.next_task()`
        if self.scene.need_proxy:
            proxy_conf = requests.get('http://localhost:8833/proxy/random')
            if proxy_conf.status_code == 200:
                proxy_conf = proxy_conf.json()
                if 'details' not in proxy_conf:
                    print(proxy_conf)
                    del proxy_conf['cookies']
                    del proxy_conf['useragent']
                    self.scene.configure(proxy_conf)
        else:
            self.scene.configure()
        # set scene task
        self.scene.beginScene(task)
        # do until scene_inst can be iterated
        while True:
            # try - except must be INSIDE the cycle - this is cause why I can't put it into the while condition
            try:
                # If false - stop
                if not next(self.scene):
                    print('end task')
                    break
            except ProxyChangeException:
                if self.scene.need_proxy:
                    self.proxyChange(task['_id'])
                else:
                    self.report(task['_id'], 'Connection error!', False, False)


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
        Starter(**params)
    elif 'exec' in params:
        _exec = params['exec']
        del params['exec']
        run_exec(_exec, **params)
