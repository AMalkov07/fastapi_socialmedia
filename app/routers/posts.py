#from .. import models, schemas, utils
import models
import schemas
from fastapi import FastAPI, Response, Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
import database
import oauth2

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
# the Limit & skip & search variables can be automatically set by our user by adding: ?Limit=<val> or ?Limit=<val>&Skip=<val> or ?Search=<val> (we do NOT need to put quotes around the value for the Search parameter)
def get_posts(db: Session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user), Limit: int = 10, Skip: int = 0, Search: Optional[str] = ""):
    # we are creating a query the the post model, and the .all() means that we want all of the found data
    # note that we are reffering to the table we want to query by using the class defined in models
    # the .filter function will essentially make is so that we only return rows in which the title column contains the Search string in some way, the .limit function limits the maximum amount of rows that will be returned by our query and offset will skip a certain number of rows from the top before starting to return values
    posts = db.query(models.Post).filter(models.Post.title.contains(Search)).limit(Limit).offset(Skip).all()
    return posts

@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(id: int, response: Response, db: Session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user)):
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

# the data the is being passed in is still being validated by the schemas.Post class
# the 3rd arguemtn creates a dependency which runs the oauth2.get_current_user function and it will only continue running the create_post function if the oauth2.get_current_user runs w/o any errors, also the current_user will contain the entire row from the users column associated w/ the user b/ thats what get_current_user returns
def create_post(post: schemas.PostCreate, db: Session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user)):
    # what we are doing in the next line is converting the post variable into a dictionary and then unpacking it w/ the **
    # the overall effect of the next line is to basically just create an object of type Post w/ all the info that was provided in the post variable, and we store all this info in the new_post variable
    # also, we manually add in the owner_id because we do not save this as part of the schemas.PostCreate schemas
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    # db.add adds the post to the database
    db.add(new_post)
    # db.commit commits the changes on our local dabase to the database esrver
    db.commit()
    # db.refresh is instead of the RETURN * at the end of our sql command, meaning that it essentially retrieves the post that we just commited to the database and stores it in the new_post variable
    db.refresh(new_post)
    return new_post

@router.delete("/{id}", status_code = 204)

def delete_post(id: int, response: Response, db: Session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user)):

    # remember that by default, this line just creates new SQL code, but does not actually query the database
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    # the .first() method actually queries the database for the sql query that is saved in post variable
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
        response.status_code = 404
        return {'message': "the page you are looking for does not exist"}

    # this if statements makes sure that a user is only deleting there own posts by comparing id's
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform request action")

    # the synchronized_session=False is the default config of the delete method and the delete method actually queries and deletes the correct post from the datbase
    post_query.delete(synchronize_session=False)
    db.commit()
    # delete function generally isn't supposed to return anything when successfully ran
    return

@router.put("/{id}", response_model=schemas.PostResponse)

def update_post(id: int, post: schemas.PostCreate, response: Response, db: Session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    changed_post = post_query.first()

    if not changed_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
        response.status_code = 404
        return {'message': "the page you are looking for does not exist"}

    if changed_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform request action") 

    # synchronize_sesion=False is the deafult config for updates
    # we can just pass in a dict for the first argument, we don't have to unpack it
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()
