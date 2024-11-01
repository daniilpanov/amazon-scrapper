from pydantic import BaseModel


class ShopCoreMetrics(BaseModel):
    revenue: float
    revenue_per_day: float
    affiliate_revenue: float
    affiliate_revenue_per_day: float
    shopping_mall_revenue: float
    shopping_mall_revenue_per_day: float
    items_sold: float
    items_sold_per_day: float
    self_operated_account_revenue: float
    self_operated_account_revenue_per_day: float
    avg_unit_price: float


class SellerOperatedAccount(BaseModel):
    nickname: str
    revenue: float
    followers: float


class Shop(BaseModel):
    internal_id: str
    name: str
    type: str
    # core_metrics: ShopCoreMetrics
    core_metrics: dict[str, float]
    self_operated_accounts: list[SellerOperatedAccount] | None = None
