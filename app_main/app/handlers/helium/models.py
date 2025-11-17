import datetime
from typing import Any

from pydantic import BaseModel


class BlackboxDocument(BaseModel):
    # product
    product_id: str
    domain: str
    product_title: str
    main_image_url: str
    price: float
    rating: float
    product_identifiers: dict[str, Any]
    shipping_details: dict[str, Any]
    weight: float | None
    age: int
    number_of_images: int
    variation_count: int
    # category
    category: str
    category_url: str
    rank: int
    # subcategory
    subcategory: str | None
    subcategory_rank: int | None
    subcategory_url: str | None
    # metrics
    parent_level_sales: int | None
    asin_sales: int | None
    parent_level_revenue: float | None
    asin_revenue: float | None
    parent_level_change: float | None
    asin_change: float | None
    last_year_sales: int | None
    best_sales_period: datetime.datetime | None
    sales_to_reviews: float | None
    storage_fee: dict[str, Any] | None
    # seller
    seller: str | None
    seller_region: str | None
    brand: str | None
