import importlib
import sys


def start(service: str, *args, **kwargs):
    try:
        importlib.import_module(service).run(*args, **kwargs)
    except ImportError:
        print('Fail: service', service, 'not found!')
        raise


def run_exec(executable: str, *args, **kwargs):
    try:
        exec_parts = executable.split('.')
        getattr(importlib.import_module('.'.join(exec_parts[:-1])), exec_parts[-1])(*args, **kwargs)
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
    elif 'executable' in params:
        run_exec(**params)
