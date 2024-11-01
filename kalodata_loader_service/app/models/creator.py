from pydantic import BaseModel


class CreatorCoreMetrics(BaseModel):
    revenue: float
    revenue_per_day: float
    live_revenue: float
    live_revenue_per_day: float
    video_mall_revenue: float
    video_mall_revenue_per_day: float
    items_sold: float
    items_sold_per_day: float
    shopping_mall_revenue: float
    shopping_mall_revenue_per_day: float
    avg_unit_price: float


class Creator(BaseModel):
    internal_id: str
    name: str
    followers: float
    debut_time: str
    last_30_days_products: int
    biography: str
    contacts_links: list[str]
    # core_metrics: CreatorCoreMetrics
    core_metrics: dict[str, float]
    shops_ids: list[str]
    products_ids: list[str]
