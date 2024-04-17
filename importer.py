import io
import json
from hashlib import sha256
from typing import Annotated

import fastapi
import pandas as pd
from fastapi import HTTPException, File, Form, UploadFile
from pymongo.errors import BulkWriteError
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

import database
import tasks

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
api_key = '2dBtEL2DRjO0AAQqaKLWEAN4xr4XTaqwSRyUXepJRDYEiseSs7JzfGTVLc3b0poS'
api_key_hashed = sha256(api_key.encode('utf-8')).hexdigest()


@app.post('/import/report')
async def import_report(request: Request, file: UploadFile):
    auth_token = request.headers.get('Authorization')
    if not auth_token or sha256(auth_token.encode('utf-8')).hexdigest() != api_key_hashed or auth_token != api_key:
        raise HTTPException(status_code=403, detail='Invalid API KEY')
    df = pd.read_csv(io.BytesIO(await file.read()), header=0, index_col=None, delimiter=';')
    print(df)
    return
    try:
        database.db('Keywords')['Amazon_keyword_tracker'].insert_many(list(df.T.to_dict().values()))
    except BulkWriteError:
        pass
    return Response(status_code=204)


if __name__ == '__main__':
    import uvicorn

    tasks.task_executor_thr.start()
    uvicorn.run(app, host='0.0.0.0', port=8831)
    tasks.task_executor_q.put_nowait((None, None))
    tasks.task_executor_thr.join()
