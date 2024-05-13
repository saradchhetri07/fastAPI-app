from datetime import datetime, timedelta, timezone
from fastapi import APIRouter,Depends, HTTPException,status
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from .auth import get_current_user
from passlib.context import CryptContext


class UserRequest(BaseModel):
    old_password : str 
    new_password : str = Field(min_length=6)


router=APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()

    
db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]
form_data_dependency = Annotated[OAuth2PasswordRequestForm,Depends()]
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

@router.get('/get_user')
async def get_user(db: db_dependency,user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail='Unauthorized access')
    
    user_info = db.query(Users).filter(Users.id == user.get('id')).first();
    return user_info


@router.put('/change_password',status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: db_dependency,user: user_dependency,user_request:UserRequest):
    if user is None:
        raise HTTPException(status_code=401,detail='Unauthorized user')

    #user present compage the password 
    user_present= db.query(Users).filter(Users.id == user.get('id')).first()


    if user_present is None:
        raise HTTPException(status_code=404,detail='User not found in database')    

    print(f'{user_present}')
   # bcrypt_context.verify(password, user.hashed_password)
    if  not bcrypt_context.verify(user_request.old_password, \
                                  user_present.hashed_password):
        raise HTTPException(status_code=401,detail='Old password is incorrect')
    
    user_present.hashed_password = bcrypt_context.hash(user_request.new_password)
    db.add(user_present)
    db.commit()