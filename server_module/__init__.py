from .server import start_server


def run(host='0.0.0.0', port=8830):
    start_server(host, port)
