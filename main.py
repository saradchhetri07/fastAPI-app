from fastapi import FastAPI, Depends, HTTPException, Path,status
from pydantic import Field,BaseModel
from sqlalchemy.orm import Session
from typing import Annotated
from models import Todos
import models
from database import engine, SessionLocal
from routers import auth,todos

app=FastAPI()


models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)

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

@app.get("/",status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency,todo_id: int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is not None:
       return todo_model
    raise HTTPException(status_code=404,details='Todo not found.')

@app.post("/todo",status_code=status.HTTP_200_OK)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.dict())

    db.add(todo_model)
    db.commit() 


@app.put("/todo/{todo_id}",status_code = status.HTTP_200_OK)
async def update_todo(db:db_dependency,todo_request: TodoRequest,todo_id:int= Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code = 404, details='Todo not found to update')
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.complete = todo_request.complete
    todo_model.priority = todo_request.priority
    db.add(todo_model)
    db.commit()


@app.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependency,todo_id: int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, details="Items to delete not found")
    
    db.query(Todos).filter(Todos.id == todo_id).delete()

    db.commit()
