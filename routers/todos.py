from fastapi import APIRouter, Depends, HTTPException, Path,status
from pydantic import Field,BaseModel
from sqlalchemy.orm import Session
from typing import Annotated
from models import Todos
from database import  SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext

router=APIRouter()

class TodoRequest(BaseModel):
    title: str = Field(min_length=3,max_length=20)
    description: str = Field(max_length = 50,min_length =5)
    priority: int = Field(gt=0,lt=6)
    complete: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()

    
db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]


@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,db: db_dependency, todo_request: TodoRequest):
    print('inside create todo')
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication failed')
     
    todo_model = Todos(**todo_request.dict(),owner_id = user.get('id'))

    db.add(todo_model)
    db.commit() 



@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,db: db_dependency):
    print(f'{user}')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()



@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todo(user:user_dependency,db: db_dependency,todo_id: int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.owner_id == todo_id).first()

    if todo_model is not None:
       return todo_model
    raise HTTPException(status_code=404,details='Todo not found.')



@router.put("/todo/{todo_id}",status_code = status.HTTP_200_OK)
async def update_todo(user: user_dependency,db:db_dependency,todo_request: TodoRequest,todo_id:int= Path(gt=0)):

    if user is None:
        raise HTTPException(status_code = 401,details='user is not authenticated')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id==user.get('id')).first()

    
    if todo_model is None:
        raise HTTPException(status_code = 404, details='Todo not found to update')
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.complete = todo_request.complete
    todo_model.priority = todo_request.priority
    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db:db_dependency,todo_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,details="user not validated")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, details="Items to delete not found")
    
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()

    db.commit()
