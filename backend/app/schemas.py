# backend/app/schemas.py
"""
Definición de los esquemas Pydantic para validar y serializar datos.
Estos se usan para entrada y salida en los endpoints de FastAPI.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ExcelFileBase(BaseModel):
    filename: str
    filepath: str
    filesize: int
    filetype: str

class ExcelFileCreate(ExcelFileBase):
    pass

class ExcelFileResponse(ExcelFileBase):
    id: int
    upload_date: datetime

    class Config:
        orm_mode = True


class ExcelDataBase(BaseModel):
    nombre: str
    direccion: str
    telefono: str
    producto: str
    cantidad: int
    hoja: str
    archivo_id: int

class ExcelDataCreate(ExcelDataBase):
    pass

class ExcelDataResponse(ExcelDataBase):
    id: int

    class Config:
        orm_mode = True


# Estructura general de la respuesta estandarizada
class APIResponse(BaseModel):
    status: str
    type: str
    title: str
    message: str
    data: Optional[dict] = None
    errors: Optional[dict] = None
