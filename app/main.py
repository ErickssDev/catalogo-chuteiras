from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import criar_tabelas
from app.routes import router
from dotenv import load_dotenv
import os

load_dotenv()

cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/fotos", StaticFiles(directory="app/fotos"), name="fotos")

@app.on_event("startup")
def on_startup():
    criar_tabelas()

app.include_router(router)