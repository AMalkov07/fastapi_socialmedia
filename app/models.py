# w/ sqlalchemy, we create models using python code and each model represents a table in our databae
# these models are used for creating tables if they don't already exist when we first connect to our database, and they are also used for adding rows to our tables

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP 
import database

#Note: if a table with the correct name but with different columns already exists in our database then it will NOT be updated when we start the server
class Post(database.Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, nullable=False, server_default=text('True'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # this line leverages our foreignkey constraint to allow us to use the "User" class information inside of this class
    owner = relationship("User")

class User(database.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Vote(database.Base):
    __tablename__ = "votes"

    # by setting both user_id and posts_id primary_Key to true, we create a composite primary key between them
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)