import io

import fastapi
import pandas as pd
import numpy as np
from fastapi import HTTPException, File, UploadFile
from pymongo.errors import BulkWriteError
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

import db_mongo
from config import *

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/import/{collection}')
async def import_items(request: Request, collection: str, document: UploadFile = File(...)):
    if collection == 'report':
        collection = 'keyword_tracker'
    auth_token = request.headers.get('Authorization')
    if not auth_token or sha256(auth_token.encode('utf-8')).hexdigest() != API_KEY_HASHED or auth_token != API_KEY:
        raise HTTPException(status_code=403, detail='Invalid API KEY')

    df = pd.read_csv(io.BytesIO(await document.read()), header=0, index_col=None, delimiter=';')
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]):
            try:
                df[col] = df[col].str.strip()
            except AttributeError:
                continue
            df[col] = df[col].replace({'true': True, 'false': False, 'null': None, 'NaN': np.nan})
            temp = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
            if temp.notna().any():
                df[col] = temp.replace([pd.NaT], [None])
    try:
        db_mongo.db('Keywords')[collection].insert_many(list(df.T.to_dict().values()), ordered=False)
    except BulkWriteError:
        pass
    return Response(status_code=204)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=PORT)
