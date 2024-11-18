from threading import Thread

from proxies_manager import updating, app


def run():
    import uvicorn

    upd_thr = Thread(target=updating, daemon=True)
    upd_thr.start()
    uvicorn.run(app, host='0.0.0.0', port=8833)


if __name__ == '__main__':
    run()
