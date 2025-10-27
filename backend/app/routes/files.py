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


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza los nombres de columnas: strip() + lower()
    Esto evita falsos 'columnas faltantes' por espacios o mayúsculas.
    """
    new_cols = []
    for c in df.columns:
        # Convertir cualquier tipo a string, strip y lower
        try:
            c_str = str(c).strip().lower()
        except Exception:
            c_str = str(c)
        new_cols.append(c_str)
    df.columns = new_cols
    return df


# ================================
# ENDPOINTS PRINCIPALES
# ================================

@router.post("/upload", response_model=schemas.APIResponse)
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Sube un archivo Excel, lo valida y registra sus metadatos."""

    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .xls o .xlsx")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if get_file_size_mb(file_path) > MAX_FILE_SIZE_MB:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="El archivo excede el tamaño máximo permitido")

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
    """Lee el contenido del Excel subido y valida las hojas y columnas."""

    db_file = crud.get_excel_file(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    try:
        excel_data = pd.read_excel(db_file.filepath, sheet_name=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error leyendo Excel: {e}")

    required_columns = ["nombre", "direccion", "telefono", "producto", "cantidad"]
    result = {}

    for sheet_name, df in excel_data.items():
        # Limpiar hojas completamente vacías
        if df is None or df.empty:
            result[sheet_name] = {"mensaje": "La hoja no contiene datos", "datos": []}
            continue

        # Normalizar columnas y chequear
        df = _normalize_columns(df)

        try:
            utils.validate_excel_columns(df.columns.tolist(), required_columns)
            # Seleccionar y completar valores faltantes
            df = df[required_columns].fillna("")
            # Retornar primeros 10 registros para la previsualización
            result[sheet_name] = {
                "mensaje": "Hoja válida",
                "datos": df.head(10).to_dict(orient="records"),
            }
        except HTTPException as e:
            result[sheet_name] = {"mensaje": str(e.detail), "datos": []}

    formatted_result = [
        {"nombre": sheet, "mensaje": info["mensaje"], "datos": info["datos"]}
        for sheet, info in result.items()
    ]

    return formatted_result


@router.post("/insert/{file_id}", response_model=schemas.APIResponse)
def insert_excel_data(file_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Inserta los datos del Excel validado en la base de datos."""

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
        if df is None or df.empty:
            continue

        # Normalizar columnas
        df = _normalize_columns(df)

        try:
            utils.validate_excel_columns(df.columns.tolist(), required_columns)
            df = df[required_columns].fillna("")

            # Conversión segura de tipos:
            data_objects = []
            for _, row in df.iterrows():
                # telefono como string (evitar pydantic error)
                telefono_val = row.get("telefono", "")
                telefono_val = "" if pd.isna(telefono_val) else str(telefono_val)

                # cantidad robusto (int desde float o string)
                cantidad_val = row.get("cantidad", 0)
                try:
                    cantidad_int = int(cantidad_val)
                except Exception:
                    try:
                        cantidad_int = int(float(cantidad_val))
                    except Exception:
                        cantidad_int = 0

                data_obj = schemas.ExcelDataCreate(
                    nombre=str(row.get("nombre", "")),
                    direccion=str(row.get("direccion", "")),
                    telefono=telefono_val,
                    producto=str(row.get("producto", "")),
                    cantidad=cantidad_int,
                    hoja=sheet_name,
                    archivo_id=file_id,
                )
                data_objects.append(data_obj)

            if data_objects:
                inserted = crud.insert_excel_data(db, data_objects)
                total_inserted += inserted

        except HTTPException as e:
            logger.warning(f"Hoja '{sheet_name}' inválida: {e.detail}")
            continue

    logger.info(f"{total_inserted} registros insertados del archivo {db_file.filename}")

    # Simulación de progreso (opcional)
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
    """Devuelve la lista de archivos Excel registrados en la base de datos."""
    files = crud.get_all_excel_files(db)
    serialized_files = [
        schemas.ExcelFileResponse.model_validate(f, from_attributes=True) for f in files
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
    """Elimina un archivo Excel y sus datos de la base de datos y del sistema."""
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


@router.get("/chart", response_model=schemas.APIResponse)
def get_chart_data(db: Session = Depends(get_db)):
    """Devuelve datos agregados para el gráfico de productos."""
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
