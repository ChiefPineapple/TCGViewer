"""
This module contains the SQLModel and various classes for the API
It also loads the environment variables and contains db dep
"""
import logging
import os
import sys
from enum import Enum
from typing import Annotated


from dotenv import load_dotenv
from fastapi import Depends
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM

# setting up the system logger for basic debugging and records
logging.basicConfig(
    stream=sys.stdout,  # Direct logs to standard output
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO  # Set the desired log level (DEBUG, INFO, WARNING, ERROR)
)
logger = logging.getLogger(__name__) # Get a logger instance for your module



# the user levels, (no real difference aside from the ability to create more users for now)
class Levels(str, Enum):
    """This class limits the user types"""
    ADMIN='ADMIN'
    STANDARD='STANDARD'

class Username(SQLModel):
    """This class just contains username"""
    username: str

# basic user info
class BasicUser(Username):
    """This class extends Username, adding levels"""
    level: Levels = Field(
        sa_column=Column(
            ENUM(Levels, name="levels_enum", create_type=True),
            nullable=False
        )
    )

# users table for storing log ins
class Users(BasicUser, table=True):
    """
    This class is the full users table
    username, password, level
    """
    __tablename__ = 'users'
    username: str = Field(primary_key=True)
    password: str

# class for data to update a user
class UpdateUsers(Users):
    """
    class for updating users. Extends Users,
    redefining all values except username to be optional and adding an optional new_username field
    """
    new_username: str | None = None
    password: str | None = None
    level: Levels | None = None

# basic class for status message
class Status(BaseModel):
    """This class is used for status messages, only a detail string"""
    detail: str


class Token(BaseModel):
    """This class is used for returning the jwt tokens"""
    access_token: str
    token_type: str = "bearer"

#creating database and tables
load_dotenv()
url = os.getenv('DATABASE_URL')
engine = create_engine(url)
secret_key = os.getenv('TOKEN_KEY')
SQLModel.metadata.create_all(engine) # creating database/tables

# method for getting a session, utilized by SessionDep
def get_session():
    """This returns a session to the database"""
    print("Returning session")
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
