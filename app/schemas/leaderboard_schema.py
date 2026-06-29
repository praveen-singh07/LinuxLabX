from pydantic import BaseModel


class LeaderboardResponse(BaseModel):

    rank: int

    username: str

    xp: int

    level: int

    completed_challenges: int