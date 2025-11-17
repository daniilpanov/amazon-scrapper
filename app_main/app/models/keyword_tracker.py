from pydantic import BaseModel


class KeywordTrackerTask(BaseModel):
    asins: list[str]
    searchQuery: str
    timeLimit: int
    pagesLimit: int
    destination: str = "remote"
