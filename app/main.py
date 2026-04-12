from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import criar_tabelas
from app.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/fotos", StaticFiles(directory="app/fotos"), name="fotos")

@app.on_event("startup")
def on_startup():
    criar_tabelas()

app.include_router(router)