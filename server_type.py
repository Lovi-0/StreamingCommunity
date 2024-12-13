# 13.12.24

import datetime
from pydantic import BaseModel
from typing import Optional, Dict, List


class WatchlistItem(BaseModel):
    name: str
    url: Optional[str] = None
    title_url: Optional[str] = None
    season: Optional[int] = None
    added_on: Optional[datetime.datetime] = None

class UpdateWatchlistItem(BaseModel):
    url: str = None
    season: int = None

class DownloadRequest(BaseModel):
    id: str
    slug: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None
