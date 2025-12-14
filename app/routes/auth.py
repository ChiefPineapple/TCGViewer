from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from models import users,SessionDep,logger
from sqlmodel import Session,select
from dotenv import load_dotenv
import bcrypt
import os 
#loading environment variables
load_dotenv(override=True)

#router definition
router = APIRouter(prefix="/auth", tags=["Authorization + User Management"])

#oath2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
salt = str(os.getenv('SALT')).encode('utf-8')
#endpoint for logging into the application
@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],session: SessionDep) -> dict:
    try:
        logger.info(f"Given Username: {form_data.username}")
        result = session.exec(
            select(users).where(users.username==form_data.username)
        ).all()
        if len(result) != 1:
            logger.info('No user found')
            return ({"message": f"No User ({form_data.username}) found"})
        else:
            bpass = form_data.password.encode('utf-8')
            if bcrypt.checkpw(bpass,result[0].password.encode('utf-8')):
                logger.info('Good password!')
                return {"message": f"Login successful for user: {form_data.username}"}
            else:
                logger.info('Bad password!')
                return {"message": f"Login failed for user: {form_data.username}"}
    except Exception as e:
        logger.error(f"Error Logging in: {e}")
        raise HTTPException(status_code=500, detail=f"Error Logging in: {e}")


# ROUTES FOR USER MANAGEMENT-------------------------------------------------------------------------------------------------

# function for adding a user
def add_user(user_info: users,session: Session):
    try:
        print(f"Adding users {user_info.username}")
        bpass = user_info.password.encode('utf-8') # encode the pass to bytes for hashing
        salt = bcrypt.gensalt() # generate the salt
        hash = bcrypt.hashpw(bpass,salt).decode('utf-8') # hash the pass, then decode for storage
        print(f'Hash: {hash}')
        user_info.password = str(hash) # type force to string for storage
        session.add(user_info) # add and commit it to database
        session.commit()
        print(f"Added user {user_info.username}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding user: {e}")

# add_user(users(username=os.getenv('API_User'),password=os.getenv('API_Password'),level='admin'),SessionDep)
@router.post("/create-user")
async def create_user(user_info: users, token: Annotated[str, Depends(oauth2_scheme)]):
    return {"message": f"Added user: {user_info}"}
