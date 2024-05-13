from datetime import datetime, timedelta, timezone
from fastapi import APIRouter,Depends, HTTPException, Path,status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Todos
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from .auth import get_current_user



router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()


db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

@router.get("/todo")
async def read_all_todo(user: user_dependency,db: db_dependency):
    if user is None or user.get('role') !='admin':
        raise HTTPException(status_code=401,detail='Unauthorized access')
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}")
async def delete_todo(user: user_dependency,db: db_dependency,todo_id:int=Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401,detail='Not authorized user')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).all()
    if todo_model is None:
        raise HTTPException(status_code=404,detail='Not authorized user')

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()