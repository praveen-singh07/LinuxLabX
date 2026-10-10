from pydantic import BaseModel

from app.schemas.progress import ProgressResponse
from app.schemas.xp import XPResponse


class DashboardResponse(BaseModel):
    user_id: int
    name: str
    email: str
    progress: ProgressResponse
    xp: XPResponse