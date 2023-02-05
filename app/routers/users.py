
import models
import schemas
import utils
from fastapi import FastAPI, Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List
import database

router = APIRouter()

@router.post("/users", status_code = 201, response_model=schemas.UserReturn)
def Create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):

    #we use the hash function that we created in the utils file to hash our password
    hashed_password=utils.hash(user.password)
    user.password=hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get('/users/{id}', response_model=schemas.UserReturn)
def get_user(id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User wit id: {id} does not exist")

    return user