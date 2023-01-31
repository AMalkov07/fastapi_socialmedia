# to start the server we use the uvicorn main:app command. the "app" reffers to our FastAPI variable
# running uvicorn main:app --reload will automatically restart the server anytime theres a change in the code
from fastapi import FastAPI
from fastapi.params import Body

app = FastAPI()

# this is a decorator. The decorator will be applied to the function thats directly following it
# The .get refers to the http GET request 
# the "/" refers to the path of the url that we want the return statement to be located at. 
#   in this case just want the root path which in our case is http://127.0.0.1:8000
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
@app.post("/createposts")

# the stuff in the parenthesis means that we want to extrac the data from the body of the http request
# that was sent by the client, then we want to conver that data to a python dictionary, and then we want to
# assign that dictonary to the variable "payload". We can then manipulate the "payload" variable in our function
def create_posts(payload: dict = Body(...)):
    #print(payload)
    payload["message"] = "successfully created posts"
    #return {"message": "successfully created posts\n" f"title: {payload['title']} content: {payload['content']}"}
    #return {"message": "successfully creates posts"}
    return payload