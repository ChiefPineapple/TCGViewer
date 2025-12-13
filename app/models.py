from sqlmodel import Field,Session,create_engine,SQLModel
from typing import Annotated
from enum import Enum
from fastapi import Depends
import os
from dotenv import load_dotenv

class levels(Enum):
    admin = 'admin'
    standard = 'standard'

class users(SQLModel, table=True):
    username: str = Field(primary_key=True)
    password: str
    level: levels

#creating database and tables
load_dotenv(override=True)
url = os.getenv('DATABASE_URL')
engine = create_engine(url)

def get_session():
    print("Returning session")
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]