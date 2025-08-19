from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import ALLOWED_ORIGINS
from .database import init_db
from .routers import auth, accounts


app = FastAPI(title="Account Vault API")

origins = ALLOWED_ORIGINS or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()   # thụt 4 khoảng trắng


app.include_router(auth.router)
app.include_router(accounts.router)


@app.get("/health")
def health():
    return {"ok": True}   # cũng thụt 4 khoảng trắng
