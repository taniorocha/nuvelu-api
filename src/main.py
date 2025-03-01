from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Response, Security, status
from fastapi.security import APIKeyHeader
from db import shutdown_db_client, startup_db_client
from contracts import CreateDailyValueRequest, CreateGoalRequest, CreateUserRequest, LoginRequest
from models import User
from auth import create_access_token, validate_access_token
from settings import Settings
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from fastapi.encoders import ENCODERS_BY_TYPE

ENCODERS_BY_TYPE[ObjectId] = str

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db_client(app)
    yield
    await shutdown_db_client(app)

app = FastAPI(lifespan=lifespan)
app.settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

token_key = APIKeyHeader(name="Authorization")

def authenticate(token: str = Security(token_key)):
    user = validate_access_token(token, app.settings)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return User(**user)


@app.get("/")
async def health_check():
    return {"health_check": "ok"}

@app.get("/check/token")
async def check_token(user: User = Depends(authenticate)):
    return {
        "token_status": "ok",
        "username": user.username
    }

@app.post("/users")
async def create_user(request: CreateUserRequest, response: Response):  
    user_exist = await app.db.users.find_one({ "username": request.username })
    if user_exist is not None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return { "detail": "Já existe um usuário com este username" }
    
    await app.db.users.insert_one(request.model_dump())
    response.status_code = status.HTTP_201_CREATED

    return {}

@app.post("/users/login")
async def login(request: LoginRequest, response: Response):
    user_exist = await app.db.users.find_one({ "username": request.username, "password": request.password })
    if user_exist is None:
        response.status_code = status.HTTP_404_NOT_FOUND

        return {}
    
    user = {
        "id": str(user_exist["_id"]),
        "name": user_exist["name"],
        "username": user_exist["username"],
        "cover": user_exist["cover"]
    }

    return {"token": create_access_token(user, app.settings)}

@app.get("/goals")
async def get_goals(user: User = Depends(authenticate)):
    goals = []
    async for goal in app.db.goals.find({ "user_id": user.id }):
        goals.append({
            "id": goal["_id"],
            "user_id": goal["user_id"],
            "silver": goal["silver"],
            "gold": goal["gold"],
            "diamond": goal["diamond"],
            "date": goal["date"]
        })

    return {"goals": goals}

@app.post("/goals")
async def create_goal(request: CreateGoalRequest, response: Response, user: User = Depends(authenticate)):
    user_exist = await app.db.users.find_one(ObjectId(user.id))
    if user_exist is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {}
    
    request.user_id = user.id
    request.date = str(datetime.fromisoformat(f"{request.date}-01").date())[:7]
    
    goal_exist = await app.db.goals.find_one({ "user_id": user.id, "date": request.date })
    print(goal_exist, { "user_id": user.id, "date": request.date })
    if goal_exist is not None:
        await app.db.goals.update_one({ "_id": ObjectId(goal_exist["_id"]) }, { "$set": request.model_dump() })
        return {}
    
    request.user_id = user.id
    await app.db.goals.insert_one(request.model_dump())
    response.status_code = status.HTTP_201_CREATED

    return {}

@app.get("/values")
async def get_daily_values_monthly(user: User = Depends(authenticate)):
    values = []
    # async for value in app.db.daily_values.find({ "user_id": user.id }):
    async for value in app.db.daily_values.find():
        values.append({
            "id": value["_id"],
            "user_id": value["user_id"],
            "value": value["value"],
            "date": value["date"]
        })

    return {"values": values}

@app.post("/values")
async def create_daily_value(request: CreateDailyValueRequest, response: Response, user: User = Depends(authenticate)):
    user_exist = await app.db.users.find_one(ObjectId(user.id))
    if user_exist is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {}
    
    request.user_id = user.id
    request.date = str(datetime.fromisoformat(request.date).date())
    
    goal_exist = await app.db.daily_values.find_one({ "user_id": user.id, "date": request.date })
    if goal_exist is not None:
        await app.db.daily_values.update_one({ "_id": ObjectId(goal_exist["_id"]) }, { "$set": request.model_dump() })
        return {}
    
    request.user_id = user.id
    await app.db.daily_values.insert_one(request.model_dump())
    response.status_code = status.HTTP_201_CREATED

    return {}