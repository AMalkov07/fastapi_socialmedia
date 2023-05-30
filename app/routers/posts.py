from fastapi import Response, Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import database, oauth2, models, schemas
from fastapi.responses import FileResponse

# we use router instead of app variable to connect to specific urls
router = APIRouter(
    #prefix="/posts",
    #tags are only used for the automatic documentation available at: http://localhost:8000/docs
    tags=['Posts']
)

# this function will return a specified number of the most recent posts based on a search parameter
@router.get("/posts", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # we return all the post information allong with the number of likes that the post currently has
    # limit, skip, and search variables are matched by URL query parameters
    # corresponding SQL command: SELECT posts.*, COUNT(votes.post_id) AS likes FROM posts JOIN votes ON posts.id = votes.post_id GROUP BY posts.id;
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts

# this function is used for retrieving a specific post by id
@router.get("/posts/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    # invalid post id's will return 404 Not found message
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    return post

@router.get("/postsLandingPage")
async def showPost():
    return FileResponse("htmlPages/newPost.html")

# this function is used for creating a post that will be tied to the id of the user that is logged in
@router.post("/posts", status_code = 201, response_model = schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user)):
    # we manually add in the owner_id from the authentication token because we do not save this as part of the schemas.PostCreate schemas
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    # db.refresh is instead of the RETURN * at the end of our sql command, meaning that it retrieves the post that we just commited to the database and stores it in the new_post variable
    db.refresh(new_post)
    return new_post

# this functoin is used for deleting one of the posts that the currently logged in user owns
@router.delete("/posts/{id}", status_code = 204)
def delete_post(id: int, db: Session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    # this if statements makes sure that a user is only deleting there own posts by comparing id's
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform request action")

    # the synchronized_session=False a default config of the delete method
    post_query.delete(synchronize_session=False)
    db.commit()
    # delete function generally isn't supposed to return anything when successfully ran
    return

# this function is used to update a post that the currently logged in user owns
@router.put("/posts/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, response: Response, db: Session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    changed_post = post_query.first()

    if not changed_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    if changed_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform request action") 

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()