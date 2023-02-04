from pydantic import BaseModel
from typing import Optional

# we use the pydantic BaseModel function to define the type of request that we want users to send in post/put requests
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

# Note: we don't actually have to specify the title, content, and published fields because they are inherited from PostBase
class Post(PostBase):
    title: str
    content: str
    published: bool = True