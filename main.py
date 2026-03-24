from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://postgres:post%40123@localhost:5432/demo"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name_of_task = Column(String, nullable=False)
    time_needed = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


app = FastAPI()


class TaskCreate(BaseModel):
    name_of_task: str
    time_needed: int
    completed: Optional[bool] = False


class TaskResponse(BaseModel):
    id: int
    name_of_task: str
    time_needed: int
    completed: bool

    model_config = {
        "from_attributes": True
    } 

@app.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate):
    db = SessionLocal()
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return db_task


@app.get("/tasks/", response_model=List[TaskResponse])
def get_tasks():
    db = SessionLocal()
    tasks = db.query(Task).all()
    db.close()
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    db.close()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, updated: TaskCreate):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")

    task.name_of_task = updated.name_of_task
    task.time_needed = updated.time_needed
    task.completed = updated.completed

    db.commit()
    db.refresh(task)
    db.close()
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    db.close()
    return {"message": "Task deleted"}


@app.get("/")
def home():
    return {"message": "API is working"}