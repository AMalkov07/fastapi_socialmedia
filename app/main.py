# to start the server we use the uvicorn main:app command. the "app" reffers to our FastAPI variable
# running uvicorn main:app --reload will automatically restart the server anytime theres a change in the code
from fastapi import FastAPI, Response, Depends, status, HTTPException
from fastapi.params import Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
#from . import schemas
import schemas
from typing import List
from sqlalchemy.orm import Session
#from . import models
import models
#from .database import engine, SessionLocal
import database
import utils
from routers import posts, users
#import routers.post
#import routers.users


#models.Base.metadata.create_all(bind=database.engine)
# Note: this line doesn't create a connection to the databaes (at least by itself), sqlalchemy is not able to create a direction connetion w/o some sort of driver doing it first such as our psycopg2 connection
# also, this line (i think) will check our database and see if it has the tables that are defined in models file. If they are not there, then it will create them
# Note: if a table exists then it won't be modified, meaning that if we change our model then we should delete any tables that had that were using the old model so that a new one can be created
models.database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# we don't want to have the api commands available if we are not connected to a database server so we put the connection command in a loop to ensure that that api server connects to the database
while True:
    try:
        # next line creates a connection to a database server and allows us to acces this connection through the conn variable
        # database, user, and password are all from postgressql setup
        # cursor_factory field changes some format stuff, in this case, it makes is so that queries include the column names in adition to the column values, basically making it a nice python dictionary
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='lkjhgfdsa101', cursor_factory=RealDictCursor)
        # cursor will be the variable that we access in order to use sql queries on our database
        cursor = conn.cursor()
        print("Database connection was successfull!")
        break
    except Exception as error:
        print("connecting to database failed")
        print(f'error: {error}')
        time.sleep(2)

app.include_router(posts.router)
app.include_router(users.router)


# this is a decorator. The decorator will be applied to the function thats directly following it
# The .get refers to the http GET request 
# the "/" refers to the path of the url that we want the return statement to be located at, in this case we just want the root path which in our case is http://127.0.0.1:8000
@app.get("/")
def root():
    #whatever is in passed into return will be returned back to the user/client
    #anything else in the function will also automatically run when the user/client accesses the function
    return "this is the root path of the posts application"

