from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import engine, SessionLocal

from fastapi import HTTPException


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TodoCreate(BaseModel):
    title: str

class TodoUpdate(BaseModel):
    completed: bool

@app.post("/todos")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    new_todo = models.Todo(
        title=todo.title,
        completed=False
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.get("/todos")
def get_todos(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    db_todo.completed = todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todoが見つかりません")
    db.delete(todo)
    db.commit()
    return

