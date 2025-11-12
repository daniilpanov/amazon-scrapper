from pydantic import BaseModel


class AsinSightTask(BaseModel):
    asin: str
    marketplace_id: str
    country: str
    user_id: str
