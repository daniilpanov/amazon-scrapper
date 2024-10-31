from pydantic import BaseModel


class VideoCoreMetrics(BaseModel):
    views: int
    views_per_day: int
    ad_video_ratio: float
    ad_revenue_ratio: float
    revenue: float
    revenue_per_day: float
    items_sold: float
    items_sold_per_day: float
    ad_spent: float
    new_followers: float
    new_followers_per_day: float
    ad_roas: float


class Video(BaseModel):
    internal_id: str
    name: str
    tags: list[str]
    music_info: str
    publish_date: str
    link: str
    core_metrics: VideoCoreMetrics
    creator_id: str
    product_name: str
