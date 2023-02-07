# to start the server we use the uvicorn main:app command. the "app" reffers to our FastAPI variable
# running uvicorn main:app --reload will automatically restart the server anytime theres a change in the code
from fastapi import FastAPI
import models
import database
from routers import posts, users, auth
from config import settings

#models.Base.metadata.create_all(bind=database.engine)
# Note: this line doesn't create a connection to the databaes (at least by itself), sqlalchemy is not able to create a direction connetion w/o some sort of driver doing it first such as our psycopg2 connection
# also, this line (i think) will check our database and see if it has the tables that are defined in models file. If they are not there, then it will create them
# Note: if a table exists then it won't be modified, meaning that if we change our model then we should delete any tables that had that were using the old model so that a new one can be created
models.database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# to make our router objects work in the other files, we must esentially extend the functionality of the app object by using hte .include_router function
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)


# this is a decorator. The decorator will be applied to the function thats directly following it
# The .get refers to the http GET request 
# the "/" refers to the path of the url that we want the return statement to be located at, in this case we just want the root path which in our case is http://127.0.0.1:8000
@app.get("/")
def root():
    #whatever is in passed into return will be returned back to the user/client
    #anything else in the function will also automatically run when the user/client accesses the function
    return {"message": "this is the root path of the application"}

