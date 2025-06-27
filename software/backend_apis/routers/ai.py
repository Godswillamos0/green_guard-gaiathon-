from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from groq import Groq
from database import SessionLocal
from models import Datas
from .esp32 import get_latest_data

router = APIRouter(
    tags=['ai'],
    prefix='/ai'
)

# Dependency injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
live_data_dependency = Annotated[dict, Depends(get_latest_data)]

# Environment config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"  # Assuming this is the correct model on Groq

@router.post("/insight")
async def generate_insight(db: db_dependency, ld: live_data_dependency):
    try:
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
- Time: {ld.time_stamp}

Insight:
"""

        insight = talk(prompt)
        return {"insight": insight}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def talk(question: str) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")

    client = Groq(api_key=GROQ_API_KEY)

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "user", "content": question}
            ],
            temperature=1,
            max_tokens=100,
            top_p=1,
            stream=False
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("Groq API Error:", str(e))
        raise HTTPException(status_code=400, detail="Bad Request to Groq API")
