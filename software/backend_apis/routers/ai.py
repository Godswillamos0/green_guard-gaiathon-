from typing import Annotated, Optional
from fastapi import FastAPI, Request, APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from datetime import datetime
from esp32 import get_latest_data
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


GROQ_API_KEY = "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"  # Store securely in env
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"


@router.post("/insight")
async def generate_insight(db:db_dependency, ld:live_data_dependency):
  datas = db.query(Datas).all  
  
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

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 100
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GROQ_API_URL, json=body, headers=headers)

    if response.status_code == 200:
        ai_message = response.json()["choices"][0]["message"]["content"]
        return {"suggestion": ai_message.strip()}
    else:
        return {"suggestion": "Unable to generate insight right now."}

