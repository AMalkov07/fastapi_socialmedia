from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

#url format: 'postgresql://<username>:<password>@<ip-address>/hostname>/<database_name>'
SQLALCHEM_DATABASES_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

# engine establishes a connection w/ the database
# Note:  sqlalchemy needs an underlying driver to connect to a database, for the postgresql database I am using the psycopg2 driver
engine = create_engine(SQLALCHEM_DATABASES_URL)

# sessoin allows you to actually interact w/ the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# all models extend this Base class
Base = declarative_base()

# this function is responsible for creating and desroying session to our database
# in our model, we create a new session every time a user accesses and new URL
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()