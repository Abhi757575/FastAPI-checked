import hashlib
import logging
from pkgutil import get_data
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from src.config import Config
import uuid
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from fastapi import HTTPException, status, Depends


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
ACCESS_TOKEN_EXPIRY = 3600

def generate_password_hash(password: str) -> str:
    # pre-hash to avoid bcrypt 72-byte limit
    password = hashlib.sha256(password.encode()).hexdigest()
    return password_context.hash(password)

def verify_password(password: str, hash: str) -> bool:
    password = hashlib.sha256(password.encode()).hexdigest()
    return password_context.verify(password, hash)

def create_access_token(data:dict , expiry:timedelta = timedelta(minutes=30), refresh:bool = False):

    payload = {}
    payload["user"] = data["user_uid"]
    payload['exp'] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh    

    token = jwt.encode(
        payload,
        key = Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )
    return token

def decode_token(token:str) -> dict:
    
    try:
        token_data = jwt.decode(
            jwt = token,
            key = Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
   
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
    

serializer = URLSafeTimedSerializer(Config.JWT_SECRET,
                                    salt="email-configuration")

def create_url_safe_token(data: dict, salt="email-configuration", expiration: int = 3600):
    """Serializes data into a URL-safe token."""

    token = serializer.dumps(data, salt=salt, expires_in = expiration)

    return token

def decode_url_safe_token(token:str):
    """Deserializes a URL-safe token back into data."""

    try:
        data = serializer.loads(token, max_age=3600)

        return data
    except SignatureExpired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired"
        )
    except BadSignature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )   