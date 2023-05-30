from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
import schemas, models, utils, oauth2, database
from fastapi.responses import FileResponse

router = APIRouter(tags=['Authentication'])

@router.get("/login/landingPage")
async def showLogin():
    return FileResponse("htmlPages/login.html")


@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserCredentials, db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # we check that the users password matches the one thats stored in our database using utils.verify
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # we pass in the info that we want to store in our JWT payload into the data field of our token
    access_token = oauth2.create_access_token(data = {"user_id": user.id})

    # bearer is just the classification name of this type of token
    return {"access_token": access_token, "token_type": "bearer"}