from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str

class CreateUserRequest(BaseModel):
    name: str
    username: str
    password: str
    cover: str

class CreateGoalRequest(BaseModel):
    user_id: str
    silver: float
    gold: float
    diamond: float
    date: str

class CreateDailyValueRequest(BaseModel):
    user_id: str
    value: float
    date: str