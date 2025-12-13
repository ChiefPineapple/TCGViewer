from fastapi import FastAPI
from routes.auth import router as auth_router,add_user
from models import engine,users
import os
from contextlib import asynccontextmanager
from sqlmodel import Session,SQLModel,select


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print('Starting')
        username = os.getenv("API_User")
        password = os.getenv("API_Password")
        url = os.getenv("DATABASE_URL")
        if not username or not password or not url:
            print("Environment Variables not defined")
            return  # fail silently or log warning
        SQLModel.metadata.create_all(engine) # creating database/tables
        with Session(engine) as session:
            # checking if the admin user exists
            existing = session.exec(
                select(users,users.username)
            ).all()
            if len(existing) == 1:
                print("Admin user exists")
            else:
                print("Admin user doesnt exist")
                add_user(users(username=username,password=password,level='admin'),session)
        yield
    finally:
        print('Shut Down')
    


app = FastAPI(
    title="TCGViewer API",
    description="""
This API is the backbone of the TCGViewer Project, it handles user management and web scraping to populate the database for report generation in metabase.
""",
version="0.1.0",
lifespan=lifespan
)

app.include_router(auth_router)



