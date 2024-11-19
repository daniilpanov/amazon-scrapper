from fastapi import FastAPI
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

app = FastAPI()
app.mount('/', StaticFiles(directory='./app/html'), name='html')


@app.get('/cp', response_class=FileResponse)
async def cp_show():
    return 'index.html'
