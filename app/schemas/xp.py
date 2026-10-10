from pydantic import BaseModel


class XPResponse(BaseModel):
    total_xp: int
    level: int

    model_config = {"from_attributes": True}