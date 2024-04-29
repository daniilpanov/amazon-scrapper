import importlib
import sys


def start(service: str, *args, **kwargs):
    try:
        importlib.import_module(service).run(*args, **kwargs)
    except ImportError:
        print('Fail: service not found!')


if __name__ == '__main__':
    import helpers
    params = helpers.parse_args(sys.argv)
    start(**params)
