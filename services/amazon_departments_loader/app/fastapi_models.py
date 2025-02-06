from pydantic import BaseModel


class InfoBSRForm(BaseModel):
    departments_flat_tree: dict[str, str]


class ASINsBSRForm(BaseModel):
    class ItemInfoASIN(BaseModel):
        asin: str
        title: str | None = None
        score: float | None = None
        number_in_BSR: int | None = None
        image: str | None = None

    bsr_id: str
    asins: list[ItemInfoASIN]
