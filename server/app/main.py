from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.sqlite_db import engine, Base
from app.routes import user_routes

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)