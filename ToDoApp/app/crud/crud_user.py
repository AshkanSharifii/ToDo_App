from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash

def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    # If an email was provided, update it
    if user_update.email is not None:
        db_user.email = user_update.email
    # If a password was provided, hash it and update
    if user_update.password is not None:
        db_user.hashed_password = get_password_hash(user_update.password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user