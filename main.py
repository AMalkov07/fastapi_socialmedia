# to start the server we use the uvicorn main:app command. the "app" reffers to our FastAPI variable
# running uvicorn main:app --reload will automatically restart the server anytime theres a change in the code
from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# we use the pydantic BaseModel function to define the type of request that we want users to send in Post requests
# all non-optional fields must be provided and they must be of the correct type
class Post(BaseModel):
    title: str
    content: str
    # published variable has a default value which means that the user will not be required to provide this value
    published: bool = True
    # this is an alternate way to create an optoinal field which will default to null if the user oes not provide it
    rating: Optional[int] = None

# this is a decorator. The decorator will be applied to the function thats directly following it
# The .get refers to the http GET request 
# the "/" refers to the path of the url that we want the return statement to be located at. 
#   in this case we just want the root path which in our case is http://127.0.0.1:8000
@app.get("/")

def root():
    #whatever is in passed into return will be returned back to the user/client
    #anything else in the function will also automatically run when the user/client accesses the function
    return {"message": "welcome to our api!!!!!"}

@app.get("/posts")
def get_posts():
    return {"data": "this is your data"}

# .post reffers to http POST request
# the POST request means that the user will send some data to the server and we can do whatever we want w/ it
@app.post("/createposts/any")

# the stuff in the parenthesis means that we want to extrac the data from the body of the http request
# that was sent by the client, then we want to conver that data to a python dictionary, and then we want to
# assign that dictonary to the variable "payload". We can then manipulate the "payload" variable in our function
def create_posts_any(payload: dict = Body(...)):
    payload["message"] = "successfully created posts"
    return payload


@app.post("/createposts/controlled")

# the stuff in parenthesis means that we automatically extract the data from our client post request and
# validate it against the model that we defined in the post class, and if the data type matches then it is
# assigned to the new_post variable (this variable will have the pydantic model type since post has this type), 
# if the data does not match then it will create a "type": "value_error" pydantic model type w/ more info
def create_posts_controlled(new_post: Post):
    print(new_post.published)
    # pydantic model types can be converted to dicitonaries with the .dict() function
    new_post_dict = new_post.dict()
    #new_post["message"] = "successfully created posts"
    new_post_dict["message"] = "successfully created posts!!"
    return new_post_dict