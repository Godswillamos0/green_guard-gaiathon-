from typing import Annotated, Optional
from fastapi import FastAPI, Request, APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from datetime import datetime
from .esp32 import get_latest_data
import httpx
import os

from database import SessionLocal
from sqlalchemy.orm import Session
from models import Meters, Users, Datas

router = APIRouter(
    tags=['ai'],
    prefix='/ai'
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
live_data_dependency =  Annotated[dict, Depends(get_latest_data)]


GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Store securely in env
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"


@router.post("/insight")
async def generate_insight(db:db_dependency, ld:live_data_dependency):
  datas = db.query(Datas).all()
  
  prompt = f"""
You are GreenGuard AI, a sustainability assistant.

Based on the data below, generate a short environmental insight (max 2 sentences) for the user. The tone should be practical and clear.

Past Data:
{datas}

Current:
- CO₂ Level (MQ-135): {ld.carbon_index1}
- Gas Level (MQ-2): {ld.carbon_index2}
- Status: {ld.status}
-Time: {ld.time_stamp}

Insight:
"""
  talk(prompt)

def talk(Question):
  client = Groq(api_key = GROQ_API_KEY)
  completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "user",
                "content": Question
            }
        ],
        temperature=1,
        max_tokens=100,
        top_p=1,
        stream=True,
        stop=None,
    )

  # see this part? just take it like that 
  all_words =[]
  for chunk in completion:
      all_words.append((chunk.choices[0].delta.content or ""))
  sentence = ''
  for word in all_words:
    sentence = sentence + word 
  return sentence
