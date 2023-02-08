# w/ sqlalchemy, we create models using python code and each model represents a table in our databae
# these models are used for creating tables if they don't already exist when we first connect to our database, and they are also used for adding rows to our tables

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP 
#from .database import Base
import database

# this is essentially how you create a table using sqlalchemy
# Note: this code is mostly used to create a new table, if a table w/ the specified name doesn't already exist
# the database.Base extension is necessary for any sqlalchemy table creation classes
class Post(database.Base):
    __tablename__ = "posts"

    # nullable controlls weather or not a field can be left empty (false means it cannot be left empty)
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    # the server_default field value will appear in the Default field of the specified column
    published = Column(Boolean, nullable=False, server_default=text('True'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    # for the ForeignKey constraint, the first field is required is should first reference the __tablename__ value and then the field that you want the foreign key to reference
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # this line leverages our foreignkey constraint to esentially do a JOIN between the Post and Users table
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