from fastapi import FastAPI
from routers import auth, links
import uvicorn
from schemas.auth import UserCreate, UserRead, UserUpdate
from managers import fastapi_users, auth_backend
from config import SECRET

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/auth/users",
    tags=["auth"]
)

app.include_router(auth.router)
app.include_router(links.router)

@app.get("/")
def root():
    return {"message": "Welcome!"}

if __name__ == "__main__":
    print("Server is starting...")
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="debug")