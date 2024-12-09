from threading import Thread

from .proxies_manager import updating, app
from .config import PORT


def run():
    import uvicorn

    upd_thr = Thread(target=updating, daemon=True)
    upd_thr.start()
    uvicorn.run(app, host='0.0.0.0', port=PORT)


if __name__ == '__main__':
    run()
