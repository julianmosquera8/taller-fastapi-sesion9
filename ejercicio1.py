from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="API de Tareas Académicas")

# 1. Modelo Pydantic con validación de longitud mínima
class Tarea(BaseModel):
    titulo: str = Field(..., min_length=3, description="Título de la tarea (mínimo 3 caracteres)")
    descripcion: Optional[str] = None
    materia: str = Field(..., min_length=3, description="Nombre de la materia (mínimo 3 caracteres)")
    completada: bool = False

class TareaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3)
    descripcion: Optional[str] = None
    materia: Optional[str] = Field(None, min_length=3)
    completada: Optional[bool] = None

# Base de datos en memoria
tareas_db = {}
id_contador = 1

# 2. Endpoint para crear tarea
@app.post("/tareas", response_model=dict, status_code=201)
def crear_tarea(tarea: Tarea):
    global id_contador
    tarea_id = id_contador
    id_contador += 1
    
    # Guardamos la tarea incluyendo su ID asignado
    nueva_tarea = {"id": tarea_id, **tarea.model_dump()}
    tareas_db[tarea_id] = nueva_tarea
    return nueva_tarea

# 3. Endpoint para actualizar tarea (estado u otros campos)
@app.put("/tareas/{tarea_id}", response_model=dict)
def actualizar_tarea(tarea_id: int, tarea_actualizada: TareaUpdate):
    if tarea_id not in tareas_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    tarea_existente = tareas_db[tarea_id]
    datos_actualizacion = tarea_actualizada.model_dump(exclude_unset=True)
    
    for clave, valor in datos_actualizacion.items():
        tarea_existente[clave] = valor
        
    tareas_db[tarea_id] = tarea_existente
    return tarea_existente

# Bloque de pruebas con TestClient para verificar reglas de negocio y errores 422
if __name__ == "__main__":
    client = TestClient(app)

    print("--- PRUEBA 1: Crear tarea válida ---")
    respuesta = client.post("/tareas", json={
        "titulo": "Parcial de Cálculo",
        "descripcion": "Estudiar integrales dobles",
        "materia": "Matemáticas",
        "completada": False
    })
    print(f"Status: {respuesta.status_code}")
    print(respuesta.json())

    print("\n--- PRUEBA 2: Validar error 422 por título o materia muy corta ---")
    respuesta_invalida = client.post("/tareas", json={
        "titulo": "Hi",  # Menos de 3 caracteres -> Dispara error 422
        "materia": "Física"
    })
    print(f"Status: {respuesta_invalida.status_code}")
    print(respuesta_invalida.json())

    print("\n--- PRUEBA 3: Actualizar estado de la tarea ---")
    respuesta_update = client.put("/tareas/1", json={
        "completada": True
    })
    print(f"Status: {respuesta_update.status_code}")
    print(respuesta_update.json())