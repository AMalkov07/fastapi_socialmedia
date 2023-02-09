from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# we use the pydantic BaseModel function to define the type of request that we want users to send in post/put requests, and we define what information that should be sent back to the user with get requests
# all non-optional fields must be provided and they must be of the correct type, otherwise an error will be thrown
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

# we use this schema returning information after a user creates a new account
class UserReturn(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime

    # these 2 lines are necessary when working with sqlalchemy. It essentially converts our sqlalchemy model responses to dicitonaries (this means that we can return sqlalchemy model variables)
    class Config:
        orm_mode = True

class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserReturn

    class Config:
        orm_mode = True

# we will use this schemas to print out a post response with the number of likes attached
# this is the normal response that will be returned to get post requests
class PostOut(BaseModel):
    Post: PostResponse
    likes: int

    class Config:
        orm_mode = True

class UserCredentials(BaseModel):
    # EmailStr is a type that validates that the nput was a valid email address
    email: EmailStr
    password: str


# token type should always be of type bearer
class Token(BaseModel):
    access_token: str
    token_type: str

# we use this to define what goes inside of our token payload
class TokenData(BaseModel):
    id: Optional[str]

# class for liking/unliking posts
# dir will be used to determine weather the post should be be a like or unlike
class Vote(BaseModel):
    post_id: int
    dir: int