import os, uuid
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .database import Base,engine,get_db
from .models import User,Complaint
from .schemas import RegisterIn,LoginIn,TokenOut,UserOut,ComplaintOut,ComplaintUpdate
from .security import hash_password,verify_password,create_token,current_user,staff_user
from .ai_service import analyse
from PIL import Image
import io

UPLOAD_DIR=Path(os.getenv("UPLOAD_DIR","uploads")); UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
Base.metadata.create_all(bind=engine)
app=FastAPI(title="SmartCivic API",version="1.0.0",description="Municipal issue reporting and triage API")
origins=[x.strip() for x in os.getenv("FRONTEND_ORIGINS","http://localhost:5173,http://127.0.0.1:5173").split(",")]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.mount("/uploads",StaticFiles(directory=str(UPLOAD_DIR)),name="uploads")
@app.get("/")
def root(): return {"name":"SmartCivic API","docs":"/docs","status":"running"}
@app.get("/api/health")
def health(): return {"status":"ok","service":"smartcivic-api"}
@app.post("/api/auth/register",response_model=TokenOut)
def register(payload:RegisterIn,db:Session=Depends(get_db)):
    email=payload.email.lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,"Email is already registered")
    role=payload.role.upper()
    if role not in ("CITIZEN","OFFICER","ADMIN"): raise HTTPException(422,"Invalid role")
    # Role selection is enabled only for academic demonstration. Lock this to CITIZEN in production.
    user=User(full_name=payload.full_name.strip(),email=email,password_hash=hash_password(payload.password),role=role)
    db.add(user);db.commit();db.refresh(user)
    return {"access_token":create_token(user),"user":user}
@app.post("/api/auth/login",response_model=TokenOut)
def login(payload:LoginIn,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==payload.email.lower()))
    if not user or not verify_password(payload.password,user.password_hash): raise HTTPException(401,"Incorrect email or password")
    return {"access_token":create_token(user),"user":user}
@app.get("/api/auth/me",response_model=UserOut)
def me(user:User=Depends(current_user)): return user
def serialize(c): return c
@app.post("/api/complaints",response_model=ComplaintOut)
async def create_complaint(description:str=Form(...),category:str=Form(...),address:str=Form(...),latitude:float|None=Form(None),longitude:float|None=Form(None),image:UploadFile|None=File(None),user:User=Depends(current_user),db:Session=Depends(get_db)):
    if len(description.strip())<12: raise HTTPException(422,"Description must contain at least 12 characters")
    if len(address.strip())<3: raise HTTPException(422,"Please provide a valid location")
    allowed={"Pothole","Streetlight","Garbage","Water leakage","Open manhole","Damaged footpath","Other"}
    if category not in allowed: raise HTTPException(422,"Unsupported issue category")
    if (latitude is None)!=(longitude is None): raise HTTPException(422,"Latitude and longitude must be supplied together")
    image_path=None
    if image:
        if image.content_type not in ("image/jpeg","image/png","image/webp"): raise HTTPException(415,"Only JPG, PNG and WEBP images are allowed")
        raw=await image.read()
        if len(raw)>8*1024*1024: raise HTTPException(413,"Image must be smaller than 8 MB")
        try: Image.open(io.BytesIO(raw)).verify()
        except Exception: raise HTTPException(422,"Uploaded file is not a valid image")
        ext={"image/jpeg":".jpg","image/png":".png","image/webp":".webp"}[image.content_type]
        name=f"{uuid.uuid4().hex}{ext}";(UPLOAD_DIR/name).write_bytes(raw);image_path=f"/uploads/{name}"
    triage=analyse(category,description)
    ticket=f"CIV-{datetime.now(timezone.utc):%y%m%d}-{uuid.uuid4().hex[:6].upper()}"
    c=Complaint(ticket_id=ticket,reporter_id=user.id,category=category,description=description.strip(),address=address.strip(),latitude=latitude,longitude=longitude,image_path=image_path,**triage)
    db.add(c);db.commit();db.refresh(c);return c
@app.get("/api/complaints",response_model=list[ComplaintOut])
def list_complaints(user:User=Depends(current_user),db:Session=Depends(get_db)):
    q=select(Complaint).order_by(Complaint.created_at.desc())
    if user.role=="CITIZEN": q=q.where(Complaint.reporter_id==user.id)
    return list(db.scalars(q).all())
@app.patch("/api/complaints/{complaint_id}",response_model=ComplaintOut)
def update_complaint(complaint_id:int,payload:ComplaintUpdate,user:User=Depends(staff_user),db:Session=Depends(get_db)):
    c=db.get(Complaint,complaint_id)
    if not c: raise HTTPException(404,"Complaint not found")
    allowed={"SUBMITTED","UNDER_REVIEW","IN_PROGRESS","RESOLVED","REJECTED"}
    if payload.status and payload.status not in allowed: raise HTTPException(422,"Invalid complaint status")
    if payload.status: c.status=payload.status
    if payload.resolution_note is not None: c.resolution_note=payload.resolution_note
    c.updated_at=datetime.now(timezone.utc);db.commit();db.refresh(c);return c
@app.get("/api/stats")
def stats(user:User=Depends(current_user),db:Session=Depends(get_db)):
    q=select(Complaint)
    if user.role=="CITIZEN": q=q.where(Complaint.reporter_id==user.id)
    rows=list(db.scalars(q).all())
    return {"total":len(rows),"open":sum(c.status not in ("RESOLVED","REJECTED") for c in rows),"resolved":sum(c.status=="RESOLVED" for c in rows)}
