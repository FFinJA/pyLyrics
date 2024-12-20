import os
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from databases import Database


# postgresql connection string
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


# SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for the database
Base = declarative_base()

# an instance of the Database class asynchronusly
database = Database(DATABASE_URL)


