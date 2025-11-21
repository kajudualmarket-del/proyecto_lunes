# backend/app/models.py
"""
Definición de los modelos de la base de datos con SQLAlchemy.
Aquí se representan las tablas principales del sistema.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

# Modelo que representa los metadatos de los archivos Excel subidos
class ExcelFile(Base):
    """
    Modelo para almacenar metadatos de los archivos Excel subidos.
    """
    __tablename__ = "excel_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    filesize = Column(Integer, nullable=False)
    filetype = Column(String(255), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())

# Modelo que representa cada fila de datos proveniente de un Excel
class ExcelData(Base):
    """
    Modelo para almacenar los datos de cada fila de los Excel validados.
    """
    __tablename__ = "excel_data"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    direccion = Column(String(255), nullable=False)
    telefono = Column(String(100), nullable=False)
    producto = Column(String(255), nullable=False)
    cantidad = Column(Integer, nullable=False)
    hoja = Column(String(100), nullable=False)  # nombre de la hoja de Excel
    archivo_id = Column(Integer, nullable=False)
