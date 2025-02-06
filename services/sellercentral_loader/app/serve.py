from fastapi import FastAPI
from .sellercentral_router import router

app = FastAPI()
app.include_router(router)
