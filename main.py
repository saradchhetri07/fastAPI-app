from fastapi import FastAPI, Depends, HTTPException, Path,status
from pydantic import Field,BaseModel
from sqlalchemy.orm import Session
from typing import Annotated
from models import Todos
import models
from database import engine, SessionLocal
from routers import auth,todos,admin,user

app=FastAPI()


models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)
