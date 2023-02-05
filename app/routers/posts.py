#from .. import models, schemas, utils
import models
import schemas
from fastapi import FastAPI, Response, Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List
import database

# instead of creating our decorators w/ the FASTAPI function stored in variable app, we instead use the APIROUTER function stored in variable router, we then use the functionality of our app variable to essentially duplicate the app variable functionality in the router function
router = APIRouter(
    # adding the prefix variable allows us to no longer have to fully specify the path in our decorators, everythin inside of the prefix will automatically be added and we just have to add the path after the prefix (if nothing comes after prefix then we just put a /)
    prefix="/posts",
    #tags are only used for the automatic documentation available at: http://localhost:8000/docs
    tags=['Posts']
)

@router.get("/", response_model=List[schemas.PostResponse])
# this function will return all posts
# the stuff if the parenthesese basically means that we are creating a new session by calling the get_db function in our database file and passing it to the Depends function from the fastapi library, and then we store this session in the variable called db
def get_posts(db: Session = Depends(database.get_db)):
    # we are creating a query the the post model, and the .all() means that we want all of the found data
    # note that we are reffering to the table we want to query by using the class defined in models
    posts = db.query(models.Post).all()
    return posts

@router.get("/{id}", response_model=schemas.PostResponse)
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
@router.post("/", status_code = 201, response_model = schemas.PostResponse)

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

@router.delete("/{id}", status_code = 204)

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

@router.put("/{id}", response_model=schemas.PostResponse)

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
