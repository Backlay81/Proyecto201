from pydantic import BaseModel, Field
from typing import Optional, List


class CanalResult(BaseModel):
    channelId: str
    title: Optional[str]
    subscriberCount: Optional[int]
    viewCount: Optional[int]
    videoCount: Optional[int]
    description: Optional[str]
    competencia_tipo: Optional[str]
    recurrente: Optional[bool]
    origin_keywords: Optional[str]


class KeywordResult(BaseModel):
    keyword: str
    channels: List[CanalResult]
    timestamp: Optional[str]


class NicheResult(BaseModel):
    keyword: str
    video_count: int
    avg_views: float
    total_likes: int
    total_comments: int
    automatizable: str
    automatizable_ratio: float
    videos_with_signals: int
    automatizable_signals: List[str]
    small_channels_ratio: float
    medium_channels_ratio: float
    large_channels_ratio: float
    unknown_channels_ratio: float
