from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Authorization + User Management"])

@router.get("/login")
def login():
    return {"message": "Login endpoint"}