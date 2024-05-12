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



router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


SECRET_KEY = '008453efc63acc5f2a4587946ac3eb097f405ac254fcefb3aa3677a3277b906e'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer_token = OAuth2PasswordBearer(tokenUrl='auth/token')
print(f'{oauth2_bearer_token}')



class UserRequest(BaseModel):
    email: str 
    first_name: str
    last_name: str
    password: str
    username: str
    role: str




class Token(BaseModel):
    access_token:str
    token_type: str




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()



db_dependency = Annotated[Session,Depends(get_db)]
form_data_dependency = Annotated[OAuth2PasswordRequestForm,Depends()]



async def get_current_user(token: Annotated[str,Depends(oauth2_bearer_token)]):
    try:
        print(f'{token}')
        payload = jwt.decode(token,SECRET_KEY,algorithms = [ALGORITHM])
        username:str= payload.get('sub')
        user_id:str = payload.get('id')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,details='Could not validatedd user')
        return {'username': username,'id':user_id}
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,details='Couldnot validate user')



@router.post("/")
async def createUser(db: db_dependency,create_user_model: UserRequest):
    user_model_created = Users(
        email= create_user_model.email,
        username  = create_user_model.username,
        first_name= create_user_model.first_name,
        last_name= create_user_model.last_name,
        hashed_password= bcrypt_context.hash(create_user_model.password),
        role = create_user_model.role,
        is_active = True
    )
    db.add(user_model_created)
    db.commit()


def create_access_token(username: str,user_id: int,expires_in:timedelta):
    encode = {'sub':username,'id':user_id}
    expires = datetime.now(timezone.utc) + expires_in
    encode.update({'exp': expires})
    return jwt.encode(encode,SECRET_KEY,algorithm='HS256')




def authenticate_user(userName,password,db):
    user = db.query(Users).filter(Users.username==userName).first()

    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    
    return user




@router.post("/token",response_model= Token)
async def login_for_access_token(db: db_dependency,form_data: form_data_dependency):
    print("inside login for access")
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,details='Could not validate user')

    token = create_access_token(user.username,user.id,timedelta(minutes=20))
    return {'token':token,'token_type':'bearer'}

