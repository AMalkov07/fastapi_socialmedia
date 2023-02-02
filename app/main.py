# to start the server we use the uvicorn main:app command. the "app" reffers to our FastAPI variable
# running uvicorn main:app --reload will automatically restart the server anytime theres a change in the code
from fastapi import FastAPI, Response, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

while True:
    try:
        # next line creates a connection to a database server
        # database, user, and password are all from postgressql setup
        # cursor_factory field changes some format stuff, in this case, it makes is so that queries include the
        # column names in adition to the column values, basically making it a nice python dictionary
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='lkjhgfdsa101', cursor_factory=RealDictCursor)
        # cursor will be the variable that we access in order to use sql queries from out database
        cursor = conn.cursor()
        print("Database connection was successfull!")
        break
    except Exception as error:
        print("connecting to database failed")
        print(f'error: {error}')
        time.sleep(2)


# we use the pydantic BaseModel function to define the type of request that we want users to send in Post requests
# all non-optional fields must be provided and they must be of the correct type
# this calss ends up inheriting from BaseModel
class Post(BaseModel):
    title: str
    content: str
    # published variable has a default value which means that the user will not be required to provide this value
    published: bool = True
    # this is an alternate way to create an optional field which will default to null if the user oes not provide it
    rating: Optional[int] = None

myPosts = []

def find_post(id):
    for p in myPosts:
        if p["id"] == id:
            return p

def find_index(id):
    for i, p in enumerate(myPosts):
        if p["id"] == id:
            return i

# this is a decorator. The decorator will be applied to the function thats directly following it
# The .get refers to the http GET request 
# the "/" refers to the path of the url that we want the return statement to be located at. 
#   in this case we just want the root path which in our case is http://127.0.0.1:8000
@app.get("/")

def root():
    #whatever is in passed into return will be returned back to the user/client
    #anything else in the function will also automatically run when the user/client accesses the function
    return "this is the root path of the posts application"

@app.get("/posts")
# this function will return all of the posts my returning our myPosts list
def get_posts():
    # this line simply saves a query, it doesn't actually execute it (despite the name)
    cursor.execute("""SELECT * FROM posts""")
    # this line actually executes the queyr on our database
    # we should use fetchall when we are expecting multiple post, and fetchone if we are expecting only 1 post
    posts = cursor.fetchall()
    return posts

@app.get("/posts/{id}")
# this function will get a specific post by id
# the id will be provided by the user by them accessing the url of the correct id
# ex. if user wants post with id 2 then they should go to http://127.0.0.1:8000/posts/2
# the stuff in the parenthesis insures that the id variable the the user is supposed to go to is an int 
# the response variable is for manipulating things about the response such as the error code
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
    post = cursor.fetchone()
    # this code will be for 404 not found error (if a user tries to access an id that doesn't exist)
    if not post:
        response.status_code = 404
        return {'message': f"the page you are looking for does not exist"}
    return post

# .post reffers to http POST request
# the POST request means that the user will send some data to the server and we can do whatever we want w/ it
@app.post("/posts/any")

# this is an example of a manual way to extract info from a post request into a dictionary
# the stuff in the parenthesis means that we want to extrac the data from the body of the http request
# that was sent by the client, then we want to conver that data to a python dictionary, and then we want to
# assign that dictonary to the variable "payload". We can then manipulate the "payload" variable in our function
def posts_any(payload: dict = Body(...)):
    payload["message"] = "successfully created posts"
    return payload



# the second parameter changes the default http code for this function
@app.post("/posts", status_code = 201)

# the stuff in parenthesis means that we automatically extract the data from our client post request and
# validate it against the model that we defined in the post class, and if the data type matches then it is
# assigned to the new_post variable (this variable will have the pydantic model type since post has this type) if the data does not match then it will create a "type": "value_error" pydantic model type w/ more info
def posts_controlled(post: Post):
    # we use this method (w/ the %s values) to create our sql command in order to avoid sql injections, this
    # works by essentially having the execute method sanatise our inputs by making sure there not sql code
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) Returning * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    # this will commit the added post to the database server. Without this, the new post will exist on the current instance of the database that the fastapi server is currently using, but won't be saved on database server
    conn.commit()
    return {"data": new_post}

@app.delete("/posts/{id}", status_code = 204)

def delete_post(id: int, response: Response):
    cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()

    if not deleted_post:
        response.status_code = 404
        return {'message': f"the page you are looking for does not exist"}
    # delete function generally isn't supposed to return anything when successfully ran
    return

@app.put("/posts/{id}")

def update_post(id: int, post: Post, response: Response):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id)))
    changed_post = cursor.fetchone()
    conn.commit()

    if not changed_post:
        response.status_code = 404
        return {'message': f"the page you are looking for does not exist"}

    return {'data': changed_post}