import os, jwt
from datetime import datetime,timedelta,timezone
from pwdlib import PasswordHash
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
SECRET=os.getenv("SECRET_KEY","development-only-change-this-secret")
ALGORITHM="HS256"
password_hash=PasswordHash.recommended()
oauth2=OAuth2PasswordBearer(tokenUrl="/api/auth/login")
def hash_password(password): return password_hash.hash(password)
def verify_password(password,hashed): return password_hash.verify(password,hashed)
def create_token(user):
    exp=datetime.now(timezone.utc)+timedelta(minutes=int(os.getenv("ACCESS_TOKEN_MINUTES","720")))
    return jwt.encode({"sub":str(user.id),"exp":exp},SECRET,algorithm=ALGORITHM)
def current_user(token:str=Depends(oauth2),db:Session=Depends(get_db)):
    error=HTTPException(status_code=401,detail="Invalid or expired authentication token",headers={"WWW-Authenticate":"Bearer"})
    try: payload=jwt.decode(token,SECRET,algorithms=[ALGORITHM]); uid=int(payload["sub"])
    except Exception: raise error
    user=db.get(User,uid)
    if not user: raise error
    return user
def staff_user(user:User=Depends(current_user)):
    if user.role not in ("OFFICER","ADMIN"): raise HTTPException(status_code=403,detail="Officer or admin access required")
    return user
