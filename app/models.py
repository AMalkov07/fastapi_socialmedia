# w/ sqlalchemy, we create models using python code and each model represents a table in our databae

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP 
#from .database import Base
import database

# this is essentially how you create a table using sqlalchemy
class Post(database.Base):
    __tablename__ = "posts"

    # nullable controlls weather or not a field can be left empty (false means it cannot be left empty)
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    # the server_default field value will appear in the Default field of the specified column
    published = Column(Boolean, nullable=False, server_default=text('True'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))