from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
import models
import schemas
from auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _get_task_or_404(task_id: int, db: Session) -> models.Task:
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def _assert_can_modify(task: models.Task, user: models.User):
    if user.role != "admin" and task.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")


@router.post("/", response_model=schemas.TaskOut, status_code=201, summary="Create a new task")
def create_task(
    body: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = models.Task(
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority,
        due_date=body.due_date,
        owner_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=List[schemas.TaskOut], summary="List tasks")
def list_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role == "admin":
        return db.query(models.Task).all()
    return db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()


@router.get("/{task_id}", response_model=schemas.TaskOut, summary="Get a single task")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = _get_task_or_404(task_id, db)
    if current_user.role != "admin" and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    return task


@router.put("/{task_id}", response_model=schemas.TaskOut, summary="Update a task")
def update_task(
    task_id: int,
    body: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = _get_task_or_404(task_id, db)
    _assert_can_modify(task, current_user)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204, summary="Delete a task")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = _get_task_or_404(task_id, db)
    _assert_can_modify(task, current_user)
    db.delete(task)
    db.commit()