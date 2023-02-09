from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from config import settings
import database, models, schemas

# the tokenUrl will be the url location in which we created the token, in ourcase we validate the user and create the token at the /login url
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# for authentication we are using a JWT token
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# the data variable will contain the payload that we want the token to carry (in a dictionary format)
def create_access_token(data: dict):
    to_encode = data.copy()

    # for the expiration time, we have ot provide the exact time at which this token will expire
    # we have to make sure to use utcnow() instead of just now()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # we want the xpiration time to be part of the payload in our token so we add it to the to_encode dictionary
    to_encode.update({"exp": expire})
    
    # this function creates a jwt token, the first argument is the payload, the 2nd is the secret key, the 3rd is the algorithm we want to use
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token

def verify_access_token(token: str, credentials_exception):

    try:
        # the algorithms argument expects a list of algorithms
        # the decode function returns the payload of our token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # we should always have an id field if we decoded a valid token
        id : str = payload.get("user_id")

        if not id :
            raise credentials_exception
        
        # this validates weather or not our token payload is the same as our schemas.TokenData schema
        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exception

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Could not validate user token", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    # this returns the entire row of the users table associated with the user id imbedded in the token
    return user