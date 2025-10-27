"""
Punto de entrada principal del backend.
Inicializa FastAPI, configura las rutas, CORS, base de datos y logs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import files
import logging
import os

# Crear instancia de la aplicación
app = FastAPI(title="Excel Uploader API", version="1.0")

# ⚙️ CORS - permitir orígenes locales
origins = [
    "http://localhost:8080",  # Frontend Angular
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # permite Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear todas las tablas (si no existen)
Base.metadata.create_all(bind=engine)

# Configuración de logs
LOG_DIR = "app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Incluir las rutas del módulo de archivos
app.include_router(files.router, prefix="/files", tags=["Excel Files"])

@app.get("/")
def root():
    """Ruta base de bienvenida."""
    return {"message": "Bienvenido al backend de Excel Uploader"}
