from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#url format: 'postgresql://<username>:<password>@<ip-address>/hostname>/<database_name>'
# hard coding stuff like your password database is obviously bad and shouldn't be done in real applications
SQLALCHEM_DATABASES_URL = 'postgresql://postgres:lkjhgfdsa101@localhost/fastapi'

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
