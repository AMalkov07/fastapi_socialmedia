from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
import schemas
import models
import utils
import oauth2
import database

router = APIRouter(tags=['Authentication'])

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserCredentials, db: Session = Depends(database.get_db)):

    # remember that this line returns the entire row of data in which the condition is met, not just the column of the specified condition (equivalent to SELECT * FROM user WHERE email = user_credentials.email)
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user:
        # when dealing w/ authentication, its generally bad practice to tell the user exactly what went wrong whe denying them a log in (aka don't tell them that the user name is incorrect, just right invalid credentials so that they have to figureout weather the usrname or the password is the probelm)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # we just use the utils.verify function to check weather our user_credentials password matches the hashed password thats stored in our databas
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # we just pass the user_id in a dictionary format to our creat_access_token function b/ thats the only thing we want to have stored in our payload of the token (expiration time will be added automatically)
    access_token = oauth2.create_access_token(data = {"user_id": user.id})

    # bearer is just the classification name of this type of token
    return {"access_token": access_token, "token_type": "bearer"}