import datetime
from datetime import timezone
import jwt

from settings import Settings

ALGORITHM = 'HS256'

def create_access_token(data: dict, settings: Settings):
    print(settings.jwt_secret_key, settings.jwt_expiration_seconds)
    to_encode = data.copy()
    expiration_time = datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(seconds=settings.jwt_expiration_seconds)
    to_encode.update({"exp": expiration_time})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
    
    return encoded_jwt

def validate_access_token(token: str, settings: Settings):
    print(settings.jwt_secret_key)
    try:
        data = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        return data
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None