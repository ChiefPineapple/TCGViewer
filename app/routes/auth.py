"""
This module holds the endpoints and methods for authenticating and user management
"""

from datetime import datetime, timedelta
from typing import Annotated, List
from sqlmodel import Session, select

import bcrypt
import jwt

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import (
    SessionDep,
    BasicUser,
    Levels,
    logger,
    secret_key,
    Status,
    Token,
    UpdateUsers,
    Username,
    Users,
)

#router definition
router = APIRouter(prefix="/auth", tags=["Authorization + User Management"])

#oath2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# AUTHENTICATION

# authenticating a token
def authenticate_token(token: Annotated[str, Depends(oauth2_scheme)]):
    """This method authenticates a token or returns an error"""
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"]
        )
        logger.info("Authenticated key with info: %s %s",payload.get("username"),payload.get("level"))
        return payload
    except Exception as e:
        logger.warning("Invalid Token")
        raise HTTPException(status_code=401,detail="Invalid Token") from e

AuthDep = Annotated[Token,Depends(authenticate_token)]

# authenticating admin
def authenticate_admin(token: Annotated[str, Depends(oauth2_scheme)]):
    """This method authenticates a token and admin status or returns an error"""
    try:
        payload = authenticate_token(token)
        if payload.get("level") == Levels.ADMIN.value:
            return payload
        else:
            raise HTTPException(status_code=403,detail="Not an admin")
    except HTTPException as e:
        if e.status_code == 401:
            logger.info("Invalid Token")
            logger.warning("Invalid Token")
            raise HTTPException(status_code=401,detail="Invalid Token") from e
        else:
            logger.warning("%s is not an admin",payload.get("username"))
            raise HTTPException(status_code=403,detail="Not an admin") from e
    except Exception as e:
        logger.error("Error in Authenticate admin: %s",e)
        raise HTTPException(status_code=500, detail=f"Internal server error {e}") from e

AuthAdminDep = Annotated[Token,Depends(authenticate_admin)]

# endpoint for logging into the application
@router.post("/login", responses={
    200: {"model":Token},
    401: {"description":"Log in failed"},
    500: {"description":"Error logging in {error_code}"}
})
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],session: SessionDep)\
 -> Token:
    """"
    This endpoint handles logging in and returning a jwt to a user
    """
    try:
        # getting the user
        logger.info("Login endpoint called for %s",form_data.username)
        result = session.exec(
            select(Users).where(Users.username==form_data.username)
        ).all()
        if len(result) != 1:
            logger.info('No user found')
            return {"message": f"No User {form_data.username} found"}
        # user found, verifying the pass against the hash
        bpass = form_data.password.encode('utf-8')
        if bcrypt.checkpw(bpass,result[0].password.encode('utf-8')):
            logger.info('Good password!')
            token = create_token(result[0])
            return Token(access_token=token)
        logger.warning('Bad password!')
        raise HTTPException(status_code=401, detail="Log in failed")
    except Exception as e:
        logger.error("Error Logging in: %s",e)
        raise HTTPException(status_code=500, detail=f"Error Logging in: {e}") from e


# method for generating tokens
def create_token(user: BasicUser):
    """This method creates a jwt token and returns it"""
    try:
        logger.info("Create token for user: %s and level %s",user.username,user.level.value)
        token = jwt.encode({
            "username": user.username,
            "level": user.level.value,
            "exp": datetime.now()+timedelta(days=1)
        },secret_key,"HS256")
        #logger.info(f"Token created: {str(token)}")
        return token
    except Exception as e:
        logger.error("Error creating token: %s",e)
        raise HTTPException(status_code=500, detail=f"Error creating token: {e}") from e


# ROUTES FOR USER MANAGEMENT


# function for checking if a user exists
def check_user(username: Username, session: Session) -> bool:
    """This method checks if a user exists, returning a bool"""
    logger.info("Checking user %s",username.username)
    try:
        existing = session.exec(
            select(Users).where(Users.username == username.username)
        ).all()
        if len(existing) == 1:
            logger.info("User %s exists",username.username)
            return True
        else:
            logger.info("User %s doesn't exist",username.username)
            return False
    except Exception as e:
        logger.error("Error checking if user exists: %s",e)
        raise HTTPException(f"Error checking if user exists: {e}") from e


# function for adding a user
def add_user(user_info: Users,session: Session) -> Status:
    """This method allows the adding of a user"""
    logger.info("Add user called for %s, %s",user_info.username, user_info.level)
    try:
        if not check_user(Username(username=user_info.username),session):
            bpass = user_info.password.encode('utf-8') # encode the pass to bytes for hashing
            salt = bcrypt.gensalt() # generate the salt
            hash_ = bcrypt.hashpw(bpass,salt).decode('utf-8') # hash the pass, then decode for storage
            user_info.password = str(hash_) # type force to string for storage
            session.add(user_info) # add and commit it to database
            session.commit()
            logger.info("Added user %s",user_info.username)
            return Status(detail=f"User {user_info.username} added")
        return Status(detail=f"User {user_info.username} exists")
    except Exception as e:
        logger.error("Error adding user: %s",e)
        raise HTTPException(status_code=500, detail=f"Error adding user: {e}") from e

def initial_user(user_info: dict,session: Session):
    """This method creates the initial admin user"""
    logger.info("initial user called for level %s",Levels.ADMIN.value)
    add_user(Users(username=user_info['username'],password=user_info['password'],level=Levels.ADMIN.value),session)

@router.post("/create-user",responses={
    200:{"model":Status,"content":{"application/json":{
        "example":{"detail":"User {username} added"}
    }}},
    401:{"description":"Invalid Token"},
    403:{
        "description":"Not an admin",
        "model":Status,
        "content":{
            "application/json":{
        "example":{
            "detail":"Not an admin"}
    }}},
    500:{"description":"Internal server error {error_info}"}
})
async def create_user(
    user_info: Annotated[Users, Form()],
    session: SessionDep,
    payload: AuthAdminDep):
    """This method adds a user to the users table"""
    logger.info("%s is adding a user",payload.get("username"))
    return add_user(user_info,session)

# route for getting users
@router.get("/get-users",responses={
    200:{"model":List[BasicUser]},
    401:{"description":"Invalid Token"},
    403:{
        "description":"Not an admin",
        "model":Status,
        "content":{
            "application/json":{
        "example":{
            "detail":"Not an admin"}
    }}},
    500:{"description":"Internal server error: {error_info}"}
})
def get_users(
    payload: AuthAdminDep,
    session: SessionDep)->List[BasicUser]:
    """This returns all users"""
    try:
        logger.info("%s called get users",payload.get("username"))
        results = session.exec(select(Users)).all()
        return [BasicUser(username=user.username,level=user.level) for user in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}") from e


# route for updating a user
@router.patch("/update-user",responses={
    200:{"model":Status,"content":{
            "application/json":{
        "example":{
            "detail":"{user} updated"}
    }}},
    401:{"description":"Invalid Token"},
    403:{
        "description":"Not an admin",
        "model":Status,
        "content":{
            "application/json":{
        "example":{
            "detail":"Not an admin"}
    }}},
    404:{"description":"Error: Not Found",
        "model":Status,
        "content":{
            "application/json":{
        "example":{
            "detail":"{user} not found"}
    }}},
    500:{"description":"Internal server error: {error_info}"}
})
def update_user(user_info: Annotated[UpdateUsers,Form()], payload: AuthAdminDep,session: SessionDep):
    """This endpoint updates a user using only what's given."""
    try:
        logger.info("Update user called by %s",payload.get("username"))
        user = session.exec(select(Users).where(Users.username==user_info.username)).one_or_none()
        if not user:
            raise HTTPException(status_code=404,detail=f"{user_info.username} not found")
        update_data = user_info.model_dump(exclude_unset=True)
        if "new_username" in update_data:
            update_data["username"] = update_data.pop("new_username")
        filtered_data = {
            field: value
            for field, value in update_data.items()
            if value is not None and value != ""
        }
        for field, value in filtered_data.items():
            setattr(user, field, value)
        session.add(user)
        session.commit()
        session.refresh(user)
        return Status(detail=f"{user_info.username} updated")
    except HTTPException as e:
        logger.warning("%s not found",user_info.username)
        raise HTTPException(status_code=404,detail=f"{user_info.username} not found") from e
    except Exception as e:
        logger.error("Error in update_user %s",e)
        raise HTTPException(status_code=500,detail=f"Internal server error: {e}") from e


# route for removing a user
@router.delete("/remove-user",responses={
    200:{"model":Status,"content":{"application/json":{
        "example":{"detail":"User {username} deleted"}
    }}},
    401:{"description":"Invalid Token"},
    403:{
        "description":"Not an admin",
        "model":Status,
        "content":{
            "application/json":{
        "example":{
            "detail":"Not an admin"}
    }}},
    404:{
        "description":"User not found",
        "model":Status,
        "content":{
            "application/json":{
        "example":{
            "detail":"{user} not found"}
    }}},
    500:{"description":"Internal server error {error_info}"}
})
async def remove_user(
    username: Annotated[Username,Form()],
    payload: AuthAdminDep,
    session: SessionDep) -> Status:
    """This endpoint deletes a user"""
    logger.info("Remover called for user %s by %s",username,payload.get("username")) # logging
    try:
        # check the user exists
        if check_user(username,session):
            logger.info("User %s exists",username.username) # logging
            user = session.get(Users,username.username) # get the user
            session.delete(user) # remove the user
            session.commit() # save
            return Status(detail=f"User {username.username} deleted") # return update
        else:
            logger.warning(f"User {username.username} doesn't exist") # log
            return Status(detail=f"{username.username} not found") # return failure
    except Exception as e:
        logger.error("Error removing user: %s",e) # logging
        raise HTTPException(status_code=500,detail=f"Error removing user: {e}") from e # return error


