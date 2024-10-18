# src/bot.py

from fastapi import FastAPI, HTTPException, Query
import uvicorn
import logging

# Importar la librería LLMLingua
try:
    from LLMLingua import Optimizer  # Asegúrate de que LLMLingua tiene una clase llamada Optimizer
except ImportError:
    raise ImportError("LLMLingua no está instalado. Asegúrate de haberlo instalado correctamente.")

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLMLingua Optimizer Bot",
    description="Un bot que optimiza pre-prompts utilizando la librería LLMLingua de Microsoft.",
    version="1.0.0"
)

# Inicializar el optimizador
try:
    optimizer = Optimizer()
    logger.info("LLMLingua Optimizer inicializado correctamente.")
except Exception as e:
    logger.error(f"Error al inicializar LLMLingua Optimizer: {e}")
    raise e

@app.get("/optimize", summary="Optimiza un pre-prompt", description="Recibe un pre-prompt a través de una solicitud GET, lo procesa y devuelve una versión optimizada.")
def optimize_prompt(pre_prompt: str = Query(..., min_length=1, description="El pre-prompt que deseas optimizar")):
    """
    Endpoint para optimizar un pre-prompt.

    - **pre_prompt**: El texto del pre-prompt que se desea optimizar.
    """
    logger.info(f"Recibido pre-prompt para optimizar: {pre_prompt}")
    try:
        optimized_prompt = optimizer.optimize(pre_prompt)
        logger.info(f"Prompt optimizado: {optimized_prompt}")
        return {"optimized_prompt": optimized_prompt}
    except Exception as e:
        logger.error(f"Error al optimizar el pre-prompt: {e}")
        raise HTTPException(status_code=500, detail="Error al optimizar el pre-prompt.")

# Punto de entrada para ejecutar el servidor
if __name__ == "__main__":
    # Ejecutar el servidor en 0.0.0.0:8000 para estar disponible en la red
    uvicorn.run("bot:app", host="0.0.0.0", port=8000, reload=True)
