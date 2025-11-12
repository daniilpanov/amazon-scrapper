from pydantic import BaseModel


class HeliumBlackBoxTask(BaseModel):
    userId: int
    maxCatLevel: int
    destination: str = "remote"
