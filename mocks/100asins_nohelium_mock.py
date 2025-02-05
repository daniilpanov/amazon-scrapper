from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

app = FastAPI()
acquired = False


@app.get('/ping')
def ping():
    return {'status': 'OK'}


@app.get('/tasks/get_available/100asins')
def get_100asins_task(stage: int = 0):
    print(stage)
    return ORJSONResponse([{
        "_id": "677d909cee667d72fda4701f",
        "script": "100asins",
        "header_id": "677d8f8cee667d72fda4701e",
        "data": {
            "label": "hair gummies",
            "type": "",
            "limit": 5,
            "domain": "amazon.com"
        },
        "status": 0,
        "confirmed_status": 0,
        "stage": 1,
        "errors": [],
        "created_at": None,
        "started_at": None,
        "ended_at": None,
        "result": {},
        "taskHeader": {
            "alias": "Test #1",
        },
    }] if not acquired and stage == 1 else [])


@app.post('/tasks/acquire/100asins/677d8f8cee667d72fda4701e/677d909cee667d72fda4701f')
def acquire_100asins_task():
    global acquired
    print('Acquired!')
    acquired = True
    return {'status': 'OK'}


@app.patch('/tasks/stage/677d909cee667d72fda4701f')
async def set_stage_100asins_task(data: Request):
    print('Task stage incremented:', await data.json())
    return {'status': 'OK'}


@app.patch('/tasks/report/677d909cee667d72fda4701f')
async def report_100asins_task(data: Request):
    print('Task reported:', await data.json())
    return {'status': 'OK'}


if __name__ == '__main__':
    from uvicorn import run
    run(app, host='localhost', port=8832)

