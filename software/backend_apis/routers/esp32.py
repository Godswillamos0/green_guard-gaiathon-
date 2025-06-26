from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Request, status, HTTPException
from pydantic import BaseModel, Field
from database import SessionLocal
from sqlalchemy.orm import Session
from models import Meters, Users, Datas
from datetime import datetime


router = APIRouter(
    tags=['esp32'],
    prefix='/esp'
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DataRequest(BaseModel):
    carbon_index1:int = Field(default=None)
    carbon_index2:int = Field(default=None)
    status:str 
    time_stamp: datetime

    class Config:
        from_attributes = True


 
latest_data: Optional[Meters]=None
db_dependency = Annotated[Session, Depends(get_db)]



async def get_latest_data():
    global latest_data
    if latest_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return DataRequest.from_orm(latest_data)

@router.post('/send_data', status_code=status.HTTP_201_CREATED)
async def send_data(db: db_dependency, data: DataRequest, request:Request):
    global latest_data
    user = db.query(Users).filter(Users.id==1).first()
    now = datetime.now()
    data.time_stamp=now
    db.add(Datas(**data.dict()))
    db.commit()
    #db.refresh(SmartMeter(**data.dict()))
    latest_data = data.dict()
    body = await request.json()
    print("Received body:", body)
    
    return {
        "status":"sent"
    }

