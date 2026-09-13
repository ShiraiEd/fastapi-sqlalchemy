from typing import Annotated
from _collections_abc import Sequence
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import UserResponse, CreateUser, UpdateUser, UpdateUserResponse
from models import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

    engine.dispose()

app = FastAPI(lifespan=lifespan)
SessionDep = Annotated[Session, Depends(get_db)]

@app.post("/users/", response_model=UserResponse)
def create_user(user: CreateUser, db : SessionDep) -> User:
    db_user =User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[UserResponse])
def get_users(db: SessionDep) -> Sequence[User]:
    return db.execute(select(User)).scalars().all()

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db : SessionDep) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UpdateUserResponse)
def update_user(user_id: int, new_user: UpdateUser, db: SessionDep) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    errors: list[str] = []
    updated_model = new_user.model_dump(exclude_unset=True)
    for key, value in updated_model.items():
        current_val = getattr(user, key)
        if value == current_val:
            errors.append(key)
            pass
        setattr(user, key, value)
    if len(errors) > 0:
        error_fmt = ", ".join(errors)
        raise HTTPException(status_code=400, detail=f"Attribute{"s" if len(errors) > 1 else ""}: {{{error_fmt}}} already exists")
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}",status_code=204)
def delete_user(user_id: int, db: SessionDep):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    db.delete(user)
    db.commit()

