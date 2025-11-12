import datetime
import typing

from pydantic import BaseModel, field_validator


def _cast_iso_dt_to_dt_obj(dt: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(dt)


class AspectsResultItem(BaseModel):
    Aspect: str
    positive: int
    negative: int

    def model_dump_with_asin(self, asin, **kwargs):
        return super().model_dump(**kwargs) | {"ASIN": asin}


class AspectsResult(BaseModel):
    asin: str
    aspects: list[AspectsResultItem]


class ProductCard(BaseModel):
    root_asin: str
    marketplaceId: str
    asin: str
    redirected_from_asin: str
    title: str
    breadcrumbs: list[str] | None = None
    currentBreadcrumb: str | None = None
    description: str | None = None
    picture_url: str | None = None
    pictures_urls: list[str | None] | None = None
    price: int | float | None = None
    rating: int | float | None = None
    reviewsCount: int | None = None
    options: dict | None = None
    currentOptions: dict[str, str] | None = None
    relatedProducts: dict | None = None
    relatedVideos: list[str] | None = None
    bsr_link: str | None = None
    number_in_BSR: int | None = None


class ReviewsResultItem(BaseModel):
    asin: str
    review_id: str
    product_url: str
    date: datetime.datetime
    country: str
    name: str
    title: str
    description: str
    rating: int = 0
    helpful: int = 0
    options: typing.Any

    _cast_date = field_validator("date", mode="before")(_cast_iso_dt_to_dt_obj)
