from .server import start_server


def run(host='0.0.0.0', port=8832):
    start_server(host, port)


if __name__ == '__main__':
    run()
