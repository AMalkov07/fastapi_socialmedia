# to start the server we use the uvicorn main:app command. the "app" reffers to our FastAPI variable
# running uvicorn main:app --reload will automatically restart the server anytime theres a change in the code
from fastapi import FastAPI, Response, Depends
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

#models.Base.metadata.create_all(bind=database.engine)
# I think this line essentially creates the connection to our database by using the engine variable defined in our database file
# also, this line (i think) will check our database and seee if it has the tables that are defined in models file. If they are not there, then it will create them
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

# this is a decorator. The decorator will be applied to the function thats directly following it
# The .get refers to the http GET request 
# the "/" refers to the path of the url that we want the return statement to be located at, in this case we just want the root path which in our case is http://127.0.0.1:8000
@app.get("/")
def root():
    #whatever is in passed into return will be returned back to the user/client
    #anything else in the function will also automatically run when the user/client accesses the function
    return "this is the root path of the posts application"

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(database.get_db)):

    #.all means that we are searching for all the posts w/ the correct requirements
    posts = db.query(models.Post).all()
    return {"data": posts}


#@app.get("/posts", response_model=List[schemas.Post])
@app.get("/posts")
# this function will return all posts
def get_posts(db: Session = Depends(database.get_db)):
    posts = db.query(models.Post).all()
    return posts

#@app.get("/posts/{id}", response_model=schemas.Post)
@app.get("/posts/{id}")
def get_post(id: int, response: Response, db: Session = Depends(database.get_db)):
    # this code will be for 404 not found error (if a user tries to access an id that doesn't exist)
    # .first will just find hte first instance of the requirements being met in our database
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        response.status_code = 404
        return {'message': f"the page you are looking for does not exist"}
    return post

# .post reffers to http POST request
# the POST request means that the user will send some data to the server and we can do whatever we want w/ it
# the status_code parameter changes the default http code for this function
# the response_model parameter defines exactly what can be returned to the user. In this case, we are passing the Schemas.Post class which inherits from the BaseModel class, which means we are required to send back a dictionary that contains all of the required fields that are defined in the schemas.Post class
@app.post("/posts", status_code = 201)
#@app.post("/posts", status_code = 201, response_model = schemas.Post)

# the data the is being reseved is still being validated by the schemas.Post class
def create_post(post: schemas.Post, db: Session = Depends(database.get_db)):
    # the nex tline is a manual way to create the new+post variable
    #new_post = models.Post(title=post.title, content=post.content, published=post.published)
    # what we are doing in the next line is converting the post variable into a dictionary and then unpacking it w/ the ** (see above line to see manual way of whats going on)
    new_post = models.Post(**post.dict())
    # db.add adds the post to the database
    db.add(new_post)
    # db.commit commits the changes on our local dabase to the database esrver
    db.commit()
    # db.refresh is instead of the RETURN * at the end of our sql command, meaning that it essentially retrieves the post that we just commited to the database and stores it in the new_post variable
    db.refresh(new_post)
    return new_post

@app.delete("/posts/{id}", status_code = 204)

def delete_post(id: int, response: Response, db: Session = Depends(database.get_db)):

    # remember that by default, this line just creates an sql command and saves it in the post variable
    post = db.query(models.Post).filter(models.Post.id == id)

    # the .first() method actually queries the database for the sql query that is saved in post variable
    if not post.first():
        response.status_code = 404
        return {'message': "the page you are looking for does not exist"}

    # the synchronized_session=False is the default config of the delete method and the delete method actually queries and deletes the correct post from the datbase
    post.delete(synchronize_session=False)
    db.commit()
    # delete function generally isn't supposed to return anything when successfully ran
    return

#@app.put("/posts/{id}", response_model=schemas.Post)
@app.put("/posts/{id}")

def update_post(id: int, post: schemas.PostCreate, response: Response, db: Session = Depends(database.get_db)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    changed_post = post_query.first()

    if not changed_post:
        response.status_code = 404
        return {'message': "the page you are looking for does not exist"}

    # synchronize_sesion=False is the deafult config for updates
    # we can just pass in a dict for the first argument, we don't have to unpack it
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()