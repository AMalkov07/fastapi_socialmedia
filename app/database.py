from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from config import settings

#url format: 'postgresql://<username>:<password>@<ip-address>/hostname>/<database_name>'
# hard coding stuff like your password database is obviously bad and shouldn't be done in real applications
#SQLALCHEM_DATABASES_URL = 'postgresql://postgres:lkjhgfdsa101@localhost/fastapi'
SQLALCHEM_DATABASES_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

# engine establishes a connection w/ the database
engine = create_engine(SQLALCHEM_DATABASES_URL)

# sessoin allows you to actually interact w/ the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# all models extend a base class that is defined here
Base = declarative_base()

# sqlAlchemy Dependency
# this function essentially creates and close our connection to the database
# We will call this function every time a user accesses our API so we are essentially creating a new sessoin w/ our database w/ every API request, and then we are ending it (both the creation and closure of the session is handled by this function)
def get_db():
    # this line creates a session and assigns it to db variable
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# we arent actually using the following code in this sqlalchemy model
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
