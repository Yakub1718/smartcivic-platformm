from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
class RegisterIn(BaseModel):
    full_name:str=Field(min_length=2,max_length=120)
    email:EmailStr
    password:str=Field(min_length=8,max_length=128)
    role:str="CITIZEN"
class LoginIn(BaseModel):
    email:EmailStr
    password:str
class UserOut(BaseModel):
    id:int; full_name:str; email:EmailStr; role:str
    model_config=ConfigDict(from_attributes=True)
class TokenOut(BaseModel):
    access_token:str; token_type:str="bearer"; user:UserOut
class ComplaintOut(BaseModel):
    id:int; ticket_id:str; reporter_id:int; category:str; description:str; address:str
    latitude:float|None; longitude:float|None; image_path:str|None
    department:str; severity:str; priority:str; status:str; ai_reason:str; resolution_note:str
    created_at:datetime; updated_at:datetime
    model_config=ConfigDict(from_attributes=True)
class ComplaintUpdate(BaseModel):
    status:str|None=None
    resolution_note:str|None=Field(default=None,max_length=1000)
