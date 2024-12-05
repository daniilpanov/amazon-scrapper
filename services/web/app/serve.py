from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount('/', StaticFiles(directory='./app/html', html=True), name='html')
