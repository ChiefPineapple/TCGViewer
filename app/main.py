"""
This module is the backbone and entry point of the API
"""
import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session,create_engine

from routes.auth import router as auth_router,initial_user

# setting up the system logger for basic debugging and records
logging.basicConfig(
stream=sys.stdout,  # Direct logs to standard output
format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
datefmt='%d-%b-%y %H:%M:%S',
level=logging.INFO  # Set the desired log level (DEBUG, INFO, WARNING, ERROR)
)
logger = logging.getLogger(__name__) # Get a logger instance for your module

# startup and shut down manager
@asynccontextmanager
async def lifespan(app_: FastAPI):
    """On start, create database/tables/admin user if they don't exist"""

    try:
        logger.info("Server Starting")
        # getting relevant environment variables
        env_username = os.getenv("API_User")
        env_password = os.getenv("API_Password")
        logger.info("%s %s for username and pass",env_username, env_password)
        user_info = {"username": env_username,"password":env_password}
        url = os.getenv("DATABASE_URL")
        # checking if the environment variables are set
        if not env_username or not env_password or not url:
            logger.warning("Environment Variables not defined")
            yield  # fail silently or log warning
        try:
            url = os.getenv('DATABASE_URL')
            engine = create_engine(url)
            with Session(engine) as session:
                initial_user(user_info,session) # if it doesn't exist, add it
        except Exception as e:
            logger.error("Error adding admin user: %s",e)
            yield
        yield
    finally:
        logger.info('Shut down')

# app definition
app = FastAPI(
    title="TCGViewer API",
    description="""
This API is the backbone of the TCGViewer Project, it handles user management and web scraping to populate the database for report generation in metabase.
""",
version="1.0.0",
lifespan=lifespan
)

app.include_router(auth_router) # including the auth router

