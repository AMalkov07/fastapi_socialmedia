from pydantic import BaseModel, EmailStr
from datetime import datetime

# we use the pydantic BaseModel function to define the type of request that we want users to send in post/put requests, and we define what informatoin should be sent back to the user w/ get requests
# all non-optional fields must be provided and they must be of the correct type, otherwise an error will be thrown
class PostBase(BaseModel):
    title: str
    content: str
    # published variable has a default value which means that the user will not be required to provide this value
    published: bool = True
    # this is an alternate way to create an optional field which will default to null if the user does not provide it
    #rating: Optional[int] = None

class PostCreate(PostBase):
    pass

# Note: becaues this class inherites from postBase, title, content, and published will be included in addition to whatever fields we specify in this function
class PostResponse(PostBase):
    id: int
    created_at: datetime

    # these 2 lines are necessary when working w/ sqlalchemy. It essentially converts our sqlalchemy model responses to dicitonaries (this means that we can return sqlalchemy model variables)
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    # EmailStr is a type that validates that the nput was a valid email address
    email: EmailStr
    password: str

# we never want to send the user back there password since they should always know it already (and its hashed anyway)
class UserReturn(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str