from typing import Annotated
from _collections_abc import Sequence
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import UserResponse, CreateUser, UpdateUser, UpdateUserResponse, LoginUser, UpdatePassword
from models import User
from hash import verify_password, hash_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

    engine.dispose()

app = FastAPI(lifespan=lifespan)
SessionDep = Annotated[Session, Depends(get_db)]

@app.post("/signup/", response_model=UserResponse)
def signup(user: CreateUser, db : SessionDep) -> User:
    db_user = User(name=user.name, password=hash_password(user.password), email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login/", response_model=UserResponse)
def login(user: LoginUser, db: SessionDep) -> User:
    logged = db.execute(select(User).where(User.email == user.email)).scalar()
    if not logged:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password, logged.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return logged


@app.get("/users/", response_model=list[UserResponse])
def get_users(db: SessionDep) -> Sequence[User]:
    return db.execute(select(User)).scalars().all()

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db : SessionDep) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=UpdateUserResponse)
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
            continue
        setattr(user, key, value)
    if len(errors) > 0:
        error_fmt = ", ".join(errors)
        raise HTTPException(status_code=400, detail=f"Attribute{"s" if len(errors) > 1 else ""}: {{{error_fmt}}} already exists")
    db.commit()
    db.refresh(user)
    return user

@app.patch("/update_password/{user_id}")
def updated_password(user_id: int, password: UpdatePassword, db: SessionDep):
    user =  db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password.old_password, user.password):
        raise HTTPException(status_code=400, detail="Old password incorrect")
    if verify_password(password.new_password, user.password):
        raise HTTPException(status_code=400, detail="Password already used")
    setattr(user, "password" , hash_password(password.new_password))
    db.commit()
    db.refresh(user)
    return {"message": "Password updated"}



@app.delete("/users/{user_id}",status_code=204)
def delete_user(user_id: int, db: SessionDep):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    db.delete(user)
    db.commit()


