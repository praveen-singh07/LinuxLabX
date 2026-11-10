from datetime import date

from pydantic import BaseModel


class AdminAnalyticsDay(BaseModel):
    day: date
    active_learners: int
    activities: int
    xp_earned: int


class AdminAnalyticsResponse(BaseModel):
    start_date: date
    end_date: date
    days: int
    active_learners: int
    activities: int
    xp_earned: int
    daily: list[AdminAnalyticsDay]
