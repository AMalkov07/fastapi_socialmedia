from passlib.context import CryptContext
# this is setting up our hashing algorithm. Essentially we are telling passlib what default hashing algorithm we want to use (in this case we are using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)
