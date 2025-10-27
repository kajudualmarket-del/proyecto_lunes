"""
Operaciones CRUD sobre la base de datos.
Encapsula toda la lógica de acceso a datos usando SQLAlchemy.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas

# ------------------ ExcelFile CRUD ------------------

def create_excel_file(db: Session, file: schemas.ExcelFileCreate):
    """
    Inserta un registro de metadatos de archivo Excel en la base de datos.
    """
    db_file = models.ExcelFile(**file.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_all_excel_files(db: Session):
    """
    Devuelve todos los registros de archivos Excel cargados.
    """
    return db.query(models.ExcelFile).order_by(models.ExcelFile.upload_date.desc()).all()


def get_excel_file(db: Session, file_id: int):
    """
    Devuelve un archivo Excel por ID.
    """
    return db.query(models.ExcelFile).filter(models.ExcelFile.id == file_id).first()


def delete_excel_file(db: Session, file_id: int):
    """
    Elimina un archivo Excel y sus datos asociados.
    """
    file = db.query(models.ExcelFile).filter(models.ExcelFile.id == file_id).first()
    if file:
        db.query(models.ExcelData).filter(models.ExcelData.archivo_id == file_id).delete()
        db.delete(file)
        db.commit()
        return True
    return False


# ------------------ ExcelData CRUD ------------------

def insert_excel_data(db: Session, data_list: list[schemas.ExcelDataCreate]):
    """
    Inserta múltiples filas de datos desde un Excel.
    """
    objects = [models.ExcelData(**data.dict()) for data in data_list]
    db.bulk_save_objects(objects)
    db.commit()
    return len(objects)


def get_all_excel_data(db: Session):
    """
    Obtiene todos los datos cargados desde los Excels.
    """
    return db.query(models.ExcelData).all()


# ------------------ 📊 NUEVA FUNCIÓN PARA EL GRÁFICO ------------------

def get_chart_data(db: Session):
    """
    Devuelve datos agregados por producto para el gráfico.
    Agrupa por 'producto' y suma las cantidades.
    """
    results = (
        db.query(
            models.ExcelData.producto.label("producto"),
            func.sum(models.ExcelData.cantidad).label("total")
        )
        .group_by(models.ExcelData.producto)
        .all()
    )

    # Convertimos los resultados a una lista de diccionarios
    return [{"producto": r.producto, "total": r.total} for r in results]
