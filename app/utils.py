from passlib.context import CryptContext
# this is setting up our hashing algorithm. Essentially we are telling passlib what default hashing algorithm we want to use (in this case we are using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    # the pwd_context.verify function will automatically hash the plain_password (the first imput), and compare it to the hashed_password and return weather or not they are equal
    return pwd_context.verify(plain_password, hashed_password)