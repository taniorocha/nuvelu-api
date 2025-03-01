import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    mongo_db_str_connection = os.getenv("MONGO_DB_STR_CONNECTION")
    jwt_expiration_seconds = int(os.getenv("JWT_EXPIRATION_SECONDS"))
    jwt_secret_key = os.getenv("JWT_SECRET_KEY")