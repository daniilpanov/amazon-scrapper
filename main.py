import importlib
import sys


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
        service = params['service']
        del params['service']
        run_exec(service, **params)
    elif 'exec' in params:
        _exec = params['exec']
        del params['exec']
        run_exec(_exec, **params)
