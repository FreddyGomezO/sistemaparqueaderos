# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.config import Base, engine, SessionLocal

# ----------------------------------------------------------------------
# 🔹 Importar todos los modelos antes de crear las tablas
# ----------------------------------------------------------------------
from app.modelos import configuracion_precios
from app.modelos import vehiculo_estacionado
from app.modelos import historial_factura

# ----------------------------------------------------------------------
# 🔹 Crear tablas automáticamente (solo si no existen)
# ----------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ----------------------------------------------------------------------
# 🔹 Importar routers
# ----------------------------------------------------------------------
from app.routers import (
    configuracion_routes,
    vehiculo_routes,
    reporte_routes,
)

# ----------------------------------------------------------------------
# 🔹 Instancia principal de FastAPI
# ----------------------------------------------------------------------
app = FastAPI(
    title="Sistema de Parqueadero",
    version="1.0",
    description="API REST del sistema de parqueadero para hotel."
)

# ----------------------------------------------------------------------
# 🔹 Configuración de CORS (para permitir peticiones desde el frontend)
# ----------------------------------------------------------------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # puedes usar ["*"] si aún no tienes dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# 🔹 Registrar Routers
# ----------------------------------------------------------------------
app.include_router(configuracion_routes.router)
app.include_router(vehiculo_routes.router)
app.include_router(reporte_routes.router)

# ----------------------------------------------------------------------
# 🔹 Endpoint raíz de prueba
# ----------------------------------------------------------------------
@app.get("/")
def root():
    """
    Verifica el estado del backend y la conexión a la base de datos.
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {
            "message": "🚗 Sistema de Parqueadero funcionando correctamente",
            "db_status": "✅ Conexión a la base de datos exitosa"
        }
    except SQLAlchemyError as e:
        return {
            "message": "🚗 Sistema de Parqueadero funcionando",
            "db_status": f"❌ Error en la base de datos: {e}"
        }