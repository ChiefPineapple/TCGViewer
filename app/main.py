from fastapi import FastAPI
from routes.auth import router as auth_router,add_user
from models import engine,users,logger
import os
from contextlib import asynccontextmanager
from sqlmodel import Session,SQLModel,select

#startup and shut down manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Server Starting")
        # getting relevant environment variables
        username = os.getenv("API_User")
        password = os.getenv("API_Password")
        url = os.getenv("DATABASE_URL")
        # checking if the environment variables are set
        if not username or not password or not url:
            logger.warning("Environment Variables not defined")
            yield  # fail silently or log warning
        SQLModel.metadata.create_all(engine) # creating database/tables
        try:
            with Session(engine) as session:
                # checking if the admin user exists
                existing = session.exec(
                    select(users,users.username)
                ).all()
                if len(existing) == 1:
                    logger.info("Admin user exists")
                else:
                    logger.info("Admin user doesnt exist")
                    add_user(users(username=username,password=password,level='admin'),session) # if it doesn't exist, add it
        except Exception as e:
            logger.error(f"Error adding admin user: {e}")
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
version="0.1.0",
lifespan=lifespan
)

app.include_router(auth_router) # including the auth router



