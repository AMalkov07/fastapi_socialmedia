from passlib.context import CryptContext
# this is setting up our hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    # the pwd_context.verify function will automatically hash the plain_password and compare it to the hashed_password
    return pwd_context.verify(plain_password, hashed_password)