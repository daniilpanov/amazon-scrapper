from fastapi import FastAPI
from .google_drive_router import router

app = FastAPI()
app.include_router(router)
