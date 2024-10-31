from pydantic import BaseModel


class ProductCoreMetrics(BaseModel):
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


class Product(BaseModel):
    internal_id: str
    shop_id: str
    name: str
    category: str
    lowest_price_30d: float
    price_range: list[float]
    commission_rate: float
    core_metrics: ProductCoreMetrics
    creators_ids: list[str] | None = None
