from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from database import SessionLocal
from sqlalchemy.orm import Session
from models import Meters, Datas
from .esp32 import get_latest_data, DataRequest
from datetime import datetime, timedelta


router = APIRouter(
    tags=['carbon_meter'],
    prefix='/meter'
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
live_data_dependency =  Annotated[dict, Depends(get_latest_data)]

@router.get('/history', status_code=status.HTTP_200_OK)
async def get_data_history(db: db_dependency):
    return db.query(Datas).all()

@router.get('/live', response_model=DataRequest, status_code=status.HTTP_200_OK)
async def get_live_data(ld:live_data_dependency):
    print(ld)
    print(type(ld))
    now = datetime.now()
    if now-ld.time_stamp > timedelta(seconds=600):
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT)
    print(ld.time_stamp -now)
    return ld