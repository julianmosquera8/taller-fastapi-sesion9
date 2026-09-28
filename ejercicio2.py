from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="API de Reseñas y Calificaciones")

# 1. Modelo Pydantic con validación de calificación entre 1 y 5
class Resena(BaseModel):
    autor: str = Field(..., min_length=1, description="Nombre del autor")
    calificacion: int = Field(..., ge=1, le=5, description="Calificación obligatoria entre 1 y 5")
    comentario: Optional[str] = Field(None, description="Comentario opcional sobre el curso/producto")

# Base de datos en memoria (lista para almacenar las reseñas)
resenas_db: List[Resena] = []

# 2. Endpoint para crear/registrar una reseña
@app.post("/resenas", response_model=Resena, status_code=201)
def crear_resena(resena: Resena):
    resenas_db.append(resena)
    return resena

# 3. Endpoint para listar todas las reseñas
@app.get("/resenas", response_model=List[Resena])
def listar_resenas():
    return resenas_db

# 4. Endpoint de regla de negocio: Calcular el promedio de calificaciones
@app.get("/resenas/promedio")
def obtener_promedio_calificaciones():
    if not resenas_db:
        return {
            "promedio": 0.0,
            "total_resenas": 0,
            "mensaje": "Aún no hay reseñas registradas."
        }
    
    suma_calificaciones = sum(r.calificacion for r in resenas_db)
    promedio = suma_calificaciones / len(resenas_db)
    
    return {
        "promedio": round(promedio, 2),
        "total_resenas": len(resenas_db)
    }

# Bloque de pruebas con TestClient para verificar reglas y validaciones
if __name__ == "__main__":
    client = TestClient(app)

    print("--- PRUEBA 1: Crear reseñas válidas ---")
    r1 = client.post("/resenas", json={"autor": "Camila", "calificacion": 5, "comentario": "Excelente explicación"})
    print(r1.status_code, r1.json())
    
    r2 = client.post("/resenas", json={"autor": "Andrés", "calificacion": 4, "comentario": "Muy buen taller"})
    print(r2.status_code, r2.json())

    print("\n--- PRUEBA 2: Validar error 422 si la calificación está fuera del rango (ej. 6) ---")
    r_invalida = client.post("/resenas", json={"autor": "Pedro", "calificacion": 6, "comentario": "No permitido"})
    print(r_invalida.status_code, r_invalida.json())

    print("\n--- PRUEBA 3: Obtener el promedio de calificaciones ---")
    r_promedio = client.get("/resenas/promedio")
    print(r_promedio.status_code, r_promedio.json())