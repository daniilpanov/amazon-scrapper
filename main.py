import importlib
import sys


def start(service: str, *args, **kwargs):
    try:
        importlib.import_module(service).run(*args, **kwargs)
    except ImportError:
        print('Fail: service', service, 'not found!')


if __name__ == '__main__':
    from args_parser import parse_args
    params = parse_args(sys.argv)
    if 'service' in params and not params['service'].endswith('_service'):
        params['service'] += '_service'
    start(**params)
