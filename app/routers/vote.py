from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
import schemas, database, models, oauth2

router = APIRouter(
    prefix = "/vote",
    tags = ['Vote']
)

# this funcion used to like or unlike a specific post
@router.post("/", status_code=201)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id of {vote.post_id} doesn't exist")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    # if the dir != 0 then we are assuming that the user wants to like a post
    if vote.dir != 0 :
        # if the post is already liked then we raise an exception
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="you have already liked this post")
        new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()

        return {"message": "successfully liked the post"}
    # else we assume that the user wants to unlike a post
    else:
        # if the post isn't liked then we throw and exception
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="your specified post does not have a like")
        vote_query.delete(synchronize_session=False)
        db.commit()

        return{"message": "successfully removed like"}
        
