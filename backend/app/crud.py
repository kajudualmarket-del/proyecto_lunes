"""
Operaciones CRUD sobre la base de datos.
Encapsula toda la lógica de acceso a datos usando SQLAlchemy.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas


# ------------------ ExcelFile CRUD ------------------

# Crea un nuevo registro en la tabla ExcelFile con los metadatos del archivo subido
def create_excel_file(db: Session, file: schemas.ExcelFileCreate):
    """
    Inserta un registro de metadatos de archivo Excel en la base de datos.
    """
    db_file = models.ExcelFile(**file.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


# Obtiene todos los archivos Excel registrados en la base de datos, ordenados por fecha de carga
def get_all_excel_files(db: Session):
    """
    Devuelve todos los registros de archivos Excel cargados.
    """
    return db.query(models.ExcelFile).order_by(models.ExcelFile.upload_date.desc()).all()


# Busca un archivo Excel específico por su ID
def get_excel_file(db: Session, file_id: int):
    """
    Devuelve un archivo Excel por ID.
    """
    return db.query(models.ExcelFile).filter(models.ExcelFile.id == file_id).first()


# Elimina un archivo Excel y todos sus datos asociados en la tabla ExcelData
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

# Inserta múltiples registros de datos provenientes del archivo Excel
def insert_excel_data(db: Session, data_list: list[schemas.ExcelDataCreate]):
    """
    Inserta múltiples filas de datos desde un Excel.
    """
    objects = [models.ExcelData(**data.dict()) for data in data_list]
    db.bulk_save_objects(objects)
    db.commit()
    return len(objects)


# Obtiene todos los registros cargados en la tabla ExcelData
def get_all_excel_data(db: Session):
    """
    Obtiene todos los datos cargados desde los Excels.
    """
    return db.query(models.ExcelData).all()


# ------------------  NUEVA FUNCIÓN PARA EL GRÁFICO ------------------

# Obtiene datos agrupados por producto sumando la cantidad total de cada uno (para gráficos)
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

    # Convierte los resultados en una lista de diccionarios legibles
    return [{"producto": r.producto, "total": r.total} for r in results]

# ------------------ CRUD manual para ExcelData ------------------

def get_excel_data_by_id(db: Session, data_id: int):
    """
    Obtiene un registro específico de ExcelData por su ID.
    """
    return db.query(models.ExcelData).filter(models.ExcelData.id == data_id).first()


def create_excel_data(db: Session, data: schemas.ExcelDataCreate):
    """
    Crea un nuevo registro en ExcelData.
    """
    db_data = models.ExcelData(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


def update_excel_data(db: Session, data_id: int, data: schemas.ExcelDataCreate):
    """
    Actualiza un registro existente en ExcelData.
    """
    db_data = db.query(models.ExcelData).filter(models.ExcelData.id == data_id).first()
    if not db_data:
        return None

    for key, value in data.dict().items():
        setattr(db_data, key, value)

    db.commit()
    db.refresh(db_data)
    return db_data


def delete_excel_data(db: Session, data_id: int):
    """
    Elimina un registro de ExcelData por su ID.
    """
    db_data = db.query(models.ExcelData).filter(models.ExcelData.id == data_id).first()
    if not db_data:
        return False

    db.delete(db_data)
    db.commit()
    return True
