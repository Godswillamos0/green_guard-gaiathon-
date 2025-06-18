from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from database import SessionLocal
from sqlalchemy.orm import Session
from models import Meters
from .esp32 import get_latest_data, DataRequest
from datetime import datetime, timedelta


router = APIRouter(
    tags=['smart_meter'],
    prefix='/meter'
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]