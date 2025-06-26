from fastapi import FastAPI
import models
from routers import auth, admin, meter, users, esp32
from fastapi.middleware.cors import CORSMiddleware
from database import engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(bind=engine)

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(meter.router)
app.include_router(users.router)
app.include_router(esp32.router)


@app.get('/ping')
async def send_data():
    return {
      "status":"ping"
    }
