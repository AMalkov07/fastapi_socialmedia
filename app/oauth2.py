from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import database
import models
import schemas

# the tokenUrl will be the url location in which we created the token, in ourcase we validate the uesr and create the token at the /login url
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# for authentication we are using a jwt token. The token will contain a header (metadata), a payload (we can chooes any payload, usually 1 or 2 parts of the user data), and a signature (the signature will be an encryption of a combination of the header, payload, and secret key, this signature can be decoded w/ the secret key if needed).
# Note: the token itself is not encrypted and anyone can see the header and payload (6:46 in vod for details)

# SECRET_KEY can be any string (prefferably long and randomely generated)
# Note: we should never actually store the key in our code, this is for simplicity sake
SECRET_KEY = "supersecretkey"

# the algorithm will be used to create our signature by hashing the header, payload, and secret key
ALGORITHM = "HS256"

# we need to privde an expiration time for the token so that users have to sometimes relog in
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# the data variable will contain the payload that we want the token to carry (in a dictionary format)
def create_access_token(data: dict):
    # we manipulate the data so we create a copy of it so that we can see the original if needed
    to_encode = data.copy()

    # for the expiration time, we have ot provide the exact time at which this token will expire (we do this by taking the current time and then adding the amount of minutes that we want to token to live b4 expiring)
    # we have to make sure to use utcnow() instead of just now()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # we want the xpiration time to be part of the payload in our token so we add it to the to_encode dictionary
    to_encode.update({"exp": expire})
    
    # this function creates a jwt token, the first argument is the payload, the 2nd is the secret key, the 3rd is the algorithm we want to use
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token

def verify_access_token(token: str, credentials_exception):

    # we put the following code in a try except block b/ it can error out
    try:
        # the jwt.decode function returns the token payload
        # the 3rd argument expects a list of algorithms
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # we should always have an id field if we decoded a valid token
        id : str = payload.get("user_id")

        if not id :
            raise credentials_exception
        
        # this validates weather or not our token payload is the same as our schemas.TokenData schema
        # basically it makes sure that all the data that we add to the token when its created is still there
        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exception

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Could not validate user token", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user