from fastapi import APIRouter,FastAPI
from routes.auth import router as auth_router

app = FastAPI(
    title="TCGViewer API",
    description="""
This API is the backbone of the TCGViewer Project, it handles user management and web scraping to populate the database for report generation in metabase.
""",
version="0.1.0",
)

app.include_router(auth_router)


