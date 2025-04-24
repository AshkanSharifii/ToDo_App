from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.user import UserOut, UserUpdate
from app.crud import crud_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def get_my_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.patch("/me", response_model=UserOut)
def update_my_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_user = crud_user.update_user(db, current_user, user_update)
    return updated_user