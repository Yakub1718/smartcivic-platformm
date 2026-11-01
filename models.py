from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
def now(): return datetime.now(timezone.utc)
class User(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(primary_key=True)
    full_name:Mapped[str]=mapped_column(String(120))
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    password_hash:Mapped[str]=mapped_column(String(255))
    role:Mapped[str]=mapped_column(String(20),default="CITIZEN")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Complaint(Base):
    __tablename__="complaints"
    id:Mapped[int]=mapped_column(primary_key=True)
    ticket_id:Mapped[str]=mapped_column(String(24),unique=True,index=True)
    reporter_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    category:Mapped[str]=mapped_column(String(60))
    description:Mapped[str]=mapped_column(Text)
    address:Mapped[str]=mapped_column(String(300))
    latitude:Mapped[float|None]=mapped_column(Float,nullable=True)
    longitude:Mapped[float|None]=mapped_column(Float,nullable=True)
    image_path:Mapped[str|None]=mapped_column(String(500),nullable=True)
    department:Mapped[str]=mapped_column(String(100),default="Municipal Services")
    severity:Mapped[str]=mapped_column(String(20),default="MEDIUM")
    priority:Mapped[str]=mapped_column(String(20),default="MEDIUM")
    status:Mapped[str]=mapped_column(String(30),default="SUBMITTED")
    ai_reason:Mapped[str]=mapped_column(Text,default="")
    resolution_note:Mapped[str]=mapped_column(Text,default="")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
    reporter=relationship("User")
