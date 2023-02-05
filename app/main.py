# to start the server we use the uvicorn main:app command. the "app" reffers to our FastAPI variable
# running uvicorn main:app --reload will automatically restart the server anytime theres a change in the code
from fastapi import FastAPI, Response, Depends, status, HTTPException
from fastapi.params import Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext
import time
#from . import schemas
import schemas
from typing import List
from sqlalchemy.orm import Session
#from . import models
import models
#from .database import engine, SessionLocal
import database

# this is setting up our hashing algorithm. Essentially we are telling passlib what default hashing algorithm we want to use (in this case we are using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# this is a decorator. The decorator will be applied to the function thats directly following it
# The .get refers to the http GET request 
# the "/" refers to the path of the url that we want the return statement to be located at, in this case we just want the root path which in our case is http://127.0.0.1:8000
@app.get("/")
def root():
    #whatever is in passed into return will be returned back to the user/client
    #anything else in the function will also automatically run when the user/client accesses the function
    return "this is the root path of the posts application"

@app.get("/posts", response_model=List[schemas.PostResponse])
# this function will return all posts
# the stuff if the parenthesese basically means that we are creating a new session by calling the get_db function in our database file and passing it to the Depends function from the fastapi library, and then we store this session in the variable called db
def get_posts(db: Session = Depends(database.get_db)):
    # we are creating a query the the post model, and the .all() means that we want all of the found data
    # note that we are reffering to the table we want to query by using the class defined in models
    posts = db.query(models.Post).all()
    return posts

@app.get("/posts/{id}", response_model=schemas.PostResponse)
def get_post(id: int, response: Response, db: Session = Depends(database.get_db)):
    # .first() will just find hte first instance of the requirements being met in our database
    post = db.query(models.Post).filter(models.Post.id == id).first()

    # this code will be for 404 not found error (if a user tries to access an id that doesn't exist)
    #if not post:
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
        response.status_code = 404
        return {'message': "the page you are looking for does not exist"}
    return post

# .post refers to http POST request
# the POST request means that the user will send some data to the server and we can do whatever we want w/ it
# the status_code parameter changes the default http code for this function
# the response_model parameter defines exactly what can be returned to the user. In this case, we are passing the Schemas.Post class which inherits from the BaseModel class, which means we are required to send back a dictionary that contains all of the required fields that are defined in the schemas.Post class
@app.post("/posts", status_code = 201, response_model = schemas.PostResponse)

# the data the is being reseved is still being validated by the schemas.Post class
def create_post(post: schemas.PostCreate, db: Session = Depends(database.get_db)):
    # the next line is a manual way to create the new+post variable
    #new_post = models.Post(title=post.title, content=post.content, published=post.published)
    # what we are doing in the next line is converting the post variable into a dictionary and then unpacking it w/ the ** (see above line to see manual way of whats going on)
    # the overall effect of the next line is to basically just create an object of type Post w/ all the info that was provided in the post variable, and we store all this info in the new_post variable
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

    # remember that by default, this line just creates new SQL code, but does not actually query the database
    post = db.query(models.Post).filter(models.Post.id == id)

    # the .first() method actually queries the database for the sql query that is saved in post variable
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
        response.status_code = 404
        return {'message': "the page you are looking for does not exist"}

    # the synchronized_session=False is the default config of the delete method and the delete method actually queries and deletes the correct post from the datbase
    post.delete(synchronize_session=False)
    db.commit()
    # delete function generally isn't supposed to return anything when successfully ran
    return

@app.put("/posts/{id}", response_model=schemas.PostResponse)

def update_post(id: int, post: schemas.PostCreate, response: Response, db: Session = Depends(database.get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    changed_post = post_query.first()

    if not changed_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
        response.status_code = 404
        return {'message': "the page you are looking for does not exist"}

    # synchronize_sesion=False is the deafult config for updates
    # we can just pass in a dict for the first argument, we don't have to unpack it
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()


@app.post("/users", status_code = 201, response_model=schemas.UserReturn)
def Create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):

    # we use the pwd_context variable created at the top of this file to hash the users password
    hashed_password=pwd_context.hash(user.password)
    user.password=hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user