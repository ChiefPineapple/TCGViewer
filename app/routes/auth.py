from datetime import datetime,timedelta
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from models import basicuser, status, users,SessionDep,logger,username,secret_key,levels
from sqlmodel import Session,select
from dotenv import load_dotenv
import bcrypt
import jwt

#loading environment variables
# load_dotenv()

#router definition
router = APIRouter(prefix="/auth", tags=["Authorization + User Management"])

#oath2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

#endpoint for logging into the application
@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],session: SessionDep) -> dict:
    try:
        # getting the user
        logger.info(f"Given Username: {form_data.username}")
        result = session.exec(
            select(users).where(users.username==form_data.username)
        ).all()
        if len(result) != 1:
            logger.info('No user found')
            return ({"message": f"No User ({form_data.username}) found"})
        else:
            # user found, verifying the pass against the hash
            bpass = form_data.password.encode('utf-8')
            if bcrypt.checkpw(bpass,result[0].password.encode('utf-8')):
                logger.info('Good password!')
                token = create_token(result[0])
                return {"token": token}
            else:
                logger.info('Bad password!')
                return {"message": f"Login failed for user: {form_data.username}"}
    except Exception as e:
        logger.error(f"Error Logging in: {e}")
        raise HTTPException(status_code=500, detail=f"Error Logging in: {e}")


# method for generating tokens
def create_token(user: basicuser):
    try:
        logger.info(f"Create token for user: {user.username} and level {user.level.value}")
        logger.info(secret_key)
        token = jwt.encode({
            "username": user.username,
            "level": user.level.value,
            "exp": datetime.now()+timedelta(days=1)
        },secret_key,"HS256")
        #logger.info(f"Token created: {str(token)}")
        return token
    except Exception as e:
        logger.error(f"Error creating token: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating token: {e}")


# ROUTES FOR USER MANAGEMENT-------------------------------------------------------------------------------------------------


# function for checking if a user exists
def check_user(username: username, session: Session) -> bool:
    logger.info(f"Checking user {username.username}")
    try:
        existing = session.exec(
            select(users).where(users.username == username.username)
        ).all()
        if len(existing) == 1:
            logger.info(f"User {username.username} exists")
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"Error checking if user exists: {e}")
        raise HTTPException(f"Error checking if user exists: {e}")


# function for adding a user
def add_user(user_info: users,session: Session) -> status:
    logger.info(f"Add user called for {user_info.username}")
    try:
        if not check_user(username(username=user_info.username),session):
            bpass = user_info.password.encode('utf-8') # encode the pass to bytes for hashing
            salt = bcrypt.gensalt() # generate the salt
            hash = bcrypt.hashpw(bpass,salt).decode('utf-8') # hash the pass, then decode for storage
            user_info.password = str(hash) # type force to string for storage
            session.add(user_info) # add and commit it to database
            session.commit()
            logger.info(f"Added user {user_info.username}")
            return status(detail=f"User {user_info.username} added")
        else:
            return status(detail=f"User {user_info.username} exists")
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding user: {e}")

# add_user(users(username=os.getenv('API_User'),password=os.getenv('API_Password'),level='admin'),SessionDep)
@router.post("/create-user")
async def create_user(user_info: Annotated[users, Form()],session: SessionDep):#token: Annotated[str, Depends(oauth2_scheme)]
    return add_user(user_info,session)

# route for removing a user
@router.delete("/remove-user")
async def remove_user(username: Annotated[username,Form()],session: SessionDep) -> status:
    logger.info(f"Remover called for user {username}") # logging
    try:
        # check the user exists
        if check_user(username,session):
            logger.info(f"User {username.username} exists") # logging
            user = session.get(users,username.username) # get the user
            session.delete(user) # remove the user
            session.commit() # save
            return status(detail=f"User {username.username} deleted") # return update
        else:
            logger.info(f"User {username.username} doesn't exist") # log
            return status(detail=f"User {username.username} doesn't exist") # return failure
    except Exception as e:
        logger.error(f"Error removing user: {e}") # logging
        raise HTTPException(status_code=500,detail=f"Error removing user: {e}") # return error