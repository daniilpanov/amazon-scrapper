import io
from hashlib import sha256

import fastapi
import pandas as pd
from fastapi import HTTPException, File, UploadFile
from pymongo.errors import BulkWriteError
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

import db_mongo

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


@app.post('/import/{collection}')
async def import_tiktok(request: Request, collection: str, document: UploadFile = File(...)):
    if collection == 'report':
        collection = 'keyword_tracker'
    auth_token = request.headers.get('Authorization')
    if not auth_token or sha256(auth_token.encode('utf-8')).hexdigest() != api_key_hashed or auth_token != api_key:
        raise HTTPException(status_code=403, detail='Invalid API KEY')
    df = pd.read_csv(io.BytesIO(await document.read()), header=0, index_col=None, delimiter=';', lineterminator='\n')
    try:
        db_mongo.db('Keywords')[collection].insert_many(list(df.T.to_dict().values()), ordered=False)
    except BulkWriteError:
        pass
    return Response(status_code=204)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8831)
