# w/ sqlalchemy, we create models using python code and each model represents a table in our databae

from sqlalchemy import Column, Integer, String, Boolean
#from .database import Base
import database

class Post(database.Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, nullable=False)