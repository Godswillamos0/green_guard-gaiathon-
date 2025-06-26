from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime


class Users(Base):
    __tablename__ = 'users'
    
    id=Column(Integer, primary_key=True, index=True)
    first_name=Column(String)
    last_name=Column(String)
    username=Column(String)
    email=Column(String)
    hashed_password=Column(String)
    
    
class Meters(Base):
    __tablename__='meters'
    
    id=Column(Integer, primary_key=True, index=True)
    serial_number=Column(String)
    owner_id=Column(Integer, ForeignKey('users.id'))
    
    
class Datas(Base):
    __tablename__='datas'
    
    id=Column(Integer, primary_key=True, index=True)
    carbon_index1=Column(Integer)
    carbon_index2=Column(Integer)
    status=Column(String)
    time_stamp=Column(DateTime)
    device_id=Column(Integer, ForeignKey("meters.id"))
    
