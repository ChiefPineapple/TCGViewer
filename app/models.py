from sqlmodel import Field,Session,create_engine,SQLModel
from typing import Annotated
from pydantic import BaseModel
from enum import Enum
from fastapi import Depends
import os
from dotenv import load_dotenv
import logging
import sys

# setting up the system logger for basic debugging and records
logging.basicConfig(
    stream=sys.stdout,  # Direct logs to standard output
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO  # Set the desired log level (DEBUG, INFO, WARNING, ERROR)
)
logger = logging.getLogger(__name__) # Get a logger instance for your module

# the user levels, (no real difference aside from the ability to create more users for now)
class levels(Enum):
    admin = 'admin'
    standard = 'standard'

class username(SQLModel):
    username: str

# basic user info
class basicuser(username):
    level: levels

# users table for storing log ins
class users(basicuser, table=True):
    username: str = Field(primary_key=True)
    password: str

# basic class for status message
class status(BaseModel):
    detail: str

#creating database and tables
load_dotenv(override=True)
url = os.getenv('DATABASE_URL')
engine = create_engine(url)

# method for getting a session, utilized by SessionDep
def get_session():
    print("Returning session")
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]