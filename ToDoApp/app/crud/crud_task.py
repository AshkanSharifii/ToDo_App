from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def create_task(db: Session, task_in: TaskCreate, owner_id: int) -> Task:
    db_task = Task(
        title=task_in.title,
        day=task_in.day,
        is_completed=False,
        owner_id=owner_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_owner(db: Session, owner_id: int) -> list[Task]:
    return db.query(Task).filter(Task.owner_id == owner_id).all()

def get_task_by_id(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()

def update_task(db: Session, db_task: Task, task_update: TaskUpdate) -> Task:
    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.day is not None:
        db_task.day = task_update.day
    if task_update.is_completed is not None:
        db_task.is_completed = task_update.is_completed

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, db_task: Task) -> None:
    db.delete(db_task)
    db.commit()