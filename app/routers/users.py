from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List
import models, schemas, utils, database

router = APIRouter(
    tags=["user"]
)

# this function is used to store a new users email and hashed password in our database
@router.post("/users", status_code = 201, response_model=schemas.UserReturn)
def Create_user(user: schemas.UserCredentials, db: Session = Depends(database.get_db)):
    #we use the hash function that we created in the utils file to hash our password
    hashed_password=utils.hash(user.password)
    user.password=hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# this function can be used to get the email associated with a particular user_id
@router.get('/users/{id}', response_model=schemas.UserReturn)
def get_user(id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User wit id: {id} does not exist")

    return user