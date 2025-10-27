"""
Definición de los esquemas Pydantic para validar y serializar datos.
Estos se usan para entrada y salida en los endpoints de FastAPI.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ------------------ Esquemas para archivos Excel ------------------

# Esquema base con los campos comunes de un archivo Excel
class ExcelFileBase(BaseModel):
    filename: str
    filepath: str
    filesize: int
    filetype: str


# Esquema usado al crear un nuevo registro de archivo Excel
class ExcelFileCreate(ExcelFileBase):
    pass


# Esquema de respuesta para mostrar datos de un archivo Excel guardado
class ExcelFileResponse(ExcelFileBase):
    id: int
    upload_date: datetime

    class Config:
        from_attributes = True  # Permite mapear modelos SQLAlchemy a Pydantic (v2)


# ------------------ Esquemas para los datos del Excel ------------------

# Esquema base con las columnas que se esperan del archivo Excel
class ExcelDataBase(BaseModel):
    nombre: str
    direccion: str
    telefono: str
    producto: str
    cantidad: int
    hoja: str
    archivo_id: int


# Esquema usado al insertar nuevos registros desde un archivo Excel
class ExcelDataCreate(ExcelDataBase):
    pass


# Esquema de respuesta para mostrar los datos guardados en la base de datos
class ExcelDataResponse(ExcelDataBase):
    id: int

    class Config:
        from_attributes = True  # Compatible con Pydantic v2


# ------------------ Esquema de respuesta genérica ------------------

# Estructura estándar usada en todas las respuestas de la API
class APIResponse(BaseModel):
    status: str                
    type: str                  
    title: str                 
    message: str               
    data: Optional[dict] = None  
    errors: Optional[dict] = None  
