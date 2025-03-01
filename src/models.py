from pydantic import BaseModel

class User(BaseModel):
    id: str
    name: str
    username: str
    cover: str

class Goal(BaseModel):
    id: str
    user_id: str
    silver: float
    gold: float
    diamond: float
    date: str

class DailyValue(BaseModel):
    id: str
    user_id: str
    value: float
    date: str