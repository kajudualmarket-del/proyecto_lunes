# backend/app/utils.py
"""
Funciones utilitarias comunes para todo el backend.
Incluye la estandarización de respuestas y validaciones generales.
"""

from fastapi import HTTPException
from app.schemas import APIResponse

def response_json(
    status: str,
    type: str,
    title: str,
    message: str,
    data: dict = None,
    errors: dict = None
):
    """
    Retorna una respuesta JSON estandarizada para todos los endpoints.

    Parámetros:
        status (str): "success" o "error"
        type (str): tipo de operación (ej. 'create', 'read', 'update', 'delete')
        title (str): título de la operación
        message (str): descripción del resultado
        data (dict, opcional): datos devueltos
        errors (dict, opcional): errores detallados

    Retorna:
        dict con estructura unificada para todas las respuestas
    """
    return {
        "status": status,
        "type": type,
        "title": title,
        "message": message,
        "data": data,
        "errors": errors
    }


def validate_excel_columns(columns: list, required_columns: list):
    """
    Verifica que las columnas de un Excel coincidan con las esperadas.

    Parámetros:
        columns (list): columnas leídas desde el Excel
        required_columns (list): columnas esperadas ['nombre','direccion','telefono','producto','cantidad']

    Retorna:
        bool: True si todas las columnas existen
    """
    missing = [col for col in required_columns if col.lower() not in [c.lower() for c in columns]]
    if missing:
        raise HTTPException(status_code=400, detail=f"Columnas faltantes: {', '.join(missing)}")
    return True
