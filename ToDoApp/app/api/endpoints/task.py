from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, get_current_user
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.crud import crud_task
from app.models.user import User

from app.utils.notification_client import NotificationClient
from app.core.consul_client import ConsulClient
import os

# Initialize clients
consul_client = ConsulClient()
notification_client = NotificationClient(consul_client)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut)
def create_task(
        task_in: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task = crud_task.create_task(db, task_in, current_user.id)

    # Send notification about the new task
    try:
        notification_client.send_notification(
            current_user.id,
            f"New task created: {task.title} due on {task.day}"
        )
    except Exception as e:
        # Don't fail if notification service is unavailable
        print(f"Failed to send notification: {e}")

    return task

@router.get("/", response_model=List[TaskOut])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_task.get_tasks_by_owner(db, current_user.id)

@router.get("/{task_id}", response_model=TaskOut)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = crud_task.get_task_by_id(db, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task

@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = crud_task.get_task_by_id(db, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return crud_task.update_task(db, task, task_update)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = crud_task.get_task_by_id(db, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    crud_task.delete_task(db, task)
    return