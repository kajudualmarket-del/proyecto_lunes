"""
Rutas para la gestión de archivos Excel:
- Subir y validar archivos Excel (.xls, .xlsx)
- Leer las hojas y validar columnas
- Insertar datos en la base de datos
- Listar y eliminar archivos
"""

import os
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, utils
from dotenv import load_dotenv
from typing import List
import shutil
import time
import logging

# Cargar variables del .env raíz
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

# Directorio donde se almacenan los archivos subidos
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/app/uploads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "xls,xlsx").split(",")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

router = APIRouter()
logger = logging.getLogger(__name__)

# ================================
# Funciones auxiliares internas
# ================================

def allowed_file(filename: str) -> bool:
    """Verifica que el archivo tenga una extensión válida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size_mb(file_path: str) -> float:
    """Devuelve el tamaño de un archivo en MB."""
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


# ================================
# ENDPOINTS PRINCIPALES
# ================================

@router.post("/upload", response_model=schemas.APIResponse)
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Sube un archivo Excel, lo valida y registra sus metadatos.
    """

    # Validar extensión
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .xls o .xlsx")

    # Guardar archivo temporalmente
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Validar tamaño
    if get_file_size_mb(file_path) > MAX_FILE_SIZE_MB:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="El archivo excede el tamaño máximo permitido")

    # Registrar metadatos
    new_file = schemas.ExcelFileCreate(
        filename=file.filename,
        filepath=file_path,
        filesize=int(os.path.getsize(file_path)),
        filetype=file.content_type,
    )
    db_file = crud.create_excel_file(db, new_file)

    logger.info(f"Archivo subido correctamente: {file.filename}")

    return utils.response_json(
        status="success",
        type="upload",
        title="Subida exitosa",
        message=f"Archivo '{file.filename}' subido correctamente.",
        data={"file_id": db_file.id, "filename": db_file.filename},
    )


@router.get("/preview/{file_id}")
def preview_excel(file_id: int, db: Session = Depends(get_db)):
    """
    Lee el contenido del Excel subido y valida las hojas y columnas.
    Devuelve los datos de cada hoja válida en formato compatible con Angular.
    """

    db_file = crud.get_excel_file(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    # Cargar Excel con pandas
    try:
        excel_data = pd.read_excel(db_file.filepath, sheet_name=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error leyendo Excel: {e}")

    required_columns = ["nombre", "direccion", "telefono", "producto", "cantidad"]
    result = {}

    # Validar cada hoja
    for sheet_name, df in excel_data.items():
        if df.empty:
            result[sheet_name] = {"mensaje": "La hoja no contiene datos", "datos": []}
            continue

        # Validar columnas
        try:
            utils.validate_excel_columns(df.columns.tolist(), required_columns)
            df = df[required_columns].fillna("")
            result[sheet_name] = {"mensaje": "Hoja válida", "datos": df.head(10).to_dict(orient="records")}
        except HTTPException as e:
            result[sheet_name] = {"mensaje": str(e.detail), "datos": []}

    # 🔧 Transformar formato para Angular (lista en lugar de objeto)
    formatted_result = [
        {"nombre": sheet, "mensaje": info["mensaje"], "datos": info["datos"]}
        for sheet, info in result.items()
    ]

    return formatted_result


@router.post("/insert/{file_id}", response_model=schemas.APIResponse)
def insert_excel_data(file_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Inserta los datos del Excel validado en la base de datos.
    Simula una barra de progreso en el frontend (0 a 100%).
    """

    db_file = crud.get_excel_file(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    try:
        excel_data = pd.read_excel(db_file.filepath, sheet_name=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error leyendo Excel: {e}")

    required_columns = ["nombre", "direccion", "telefono", "producto", "cantidad"]
    total_inserted = 0

    for sheet_name, df in excel_data.items():
        if df.empty:
            continue
        try:
            utils.validate_excel_columns(df.columns.tolist(), required_columns)
            df = df[required_columns].fillna("")
            data_objects = [
                schemas.ExcelDataCreate(
                    nombre=row["nombre"],
                    direccion=row["direccion"],
                    telefono=row["telefono"],
                    producto=row["producto"],
                    cantidad=int(row["cantidad"]),
                    hoja=sheet_name,
                    archivo_id=file_id,
                )
                for _, row in df.iterrows()
            ]
            inserted = crud.insert_excel_data(db, data_objects)
            total_inserted += inserted

        except HTTPException as e:
            logger.warning(f"Hoja '{sheet_name}' inválida: {e.detail}")
            continue

    logger.info(f"{total_inserted} registros insertados del archivo {db_file.filename}")

    # Simulación de barra de carga (frontend usa eventos o polling)
    for progress in range(0, 101, 20):
        time.sleep(0.1)
        logger.info(f"Progreso de inserción: {progress}%")

    return utils.response_json(
        status="success",
        type="insert",
        title="Carga completada",
        message=f"Se insertaron {total_inserted} registros correctamente.",
        data={"total_inserted": total_inserted},
    )


@router.get("/", response_model=schemas.APIResponse)
def list_uploaded_files(db: Session = Depends(get_db)):
    """
    Devuelve la lista de archivos Excel registrados en la base de datos.
    """
    files = crud.get_all_excel_files(db)

    # ✅ FIX Pydantic serialization (convierte objetos SQLAlchemy a modelos válidos)
    serialized_files = [
        schemas.ExcelFileResponse.model_validate(f, from_attributes=True)
        for f in files
    ]

    return utils.response_json(
        status="success",
        type="list",
        title="Archivos registrados",
        message="Lista de archivos cargados",
        data={"files": serialized_files},
    )


@router.delete("/{file_id}", response_model=schemas.APIResponse)
def delete_excel_file(file_id: int, db: Session = Depends(get_db)):
    """
    Elimina un archivo Excel y sus datos de la base de datos y del sistema.
    """
    db_file = crud.get_excel_file(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    file_path = db_file.filepath
    deleted = crud.delete_excel_file(db, file_id)

    if deleted and os.path.exists(file_path):
        os.remove(file_path)

    return utils.response_json(
        status="success",
        type="delete",
        title="Eliminación completada",
        message=f"Archivo '{db_file.filename}' eliminado correctamente.",
    )


# ================================
# 📊 NUEVO ENDPOINT: Datos del gráfico
# ================================
@router.get("/chart", response_model=schemas.APIResponse)
def get_chart_data(db: Session = Depends(get_db)):
    """
    Devuelve datos agregados para el gráfico de productos.
    Suma la cantidad de cada producto registrado.
    """
    try:
        data = crud.get_chart_data(db)
        return utils.response_json(
            status="success",
            type="chart",
            title="Datos para el gráfico",
            message="Datos agregados obtenidos correctamente",
            data={"chart": data},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos del gráfico: {e}")
