from fastapi import FastAPI
import models
from routers import auth, admin, meter, users, esp32
from database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(meter.router)
app.include_router(users.router)
app.include_router(esp32.router)
