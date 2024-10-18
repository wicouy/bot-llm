# src/bot.py

from fastapi import FastAPI, HTTPException, Query
import uvicorn
import logging

# Importar la clase PromptCompressor desde llmlingua
try:
    from llmlingua import PromptCompressor
except ImportError as e:
    raise ImportError(
        "No se pudo importar 'PromptCompressor' desde 'llmlingua'. "
        "Verifica que el paquete LLMLingua esté instalado correctamente y que la clase PromptCompressor exista."
    ) from e

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="LLMLingua Prompt Compressor Bot",
    description="Un bot que comprime prompts utilizando la librería LLMLingua de Microsoft.",
    version="1.0.0"
)

# Inicializar el PromptCompressor
try:
    compressor = PromptCompressor(
        model_name="NousResearch/Llama-2-7b-hf",  # Ajusta el modelo según tus necesidades
        device_map="cuda",  # Cambia a "cpu" si no tienes GPU
        model_config={},  # Configuraciones adicionales del modelo si son necesarias
        open_api_config={},  # Configuraciones de OpenAI si son necesarias
        use_llmlingua2=False,  # Cambia a True si deseas usar llmlingua-2
        llmlingua2_config={},  # Configuraciones de llmlingua-2 si las usas
    )
    logger.info("LLMLingua PromptCompressor inicializado correctamente.")
except Exception as e:
    logger.error(f"Error al inicializar LLMLingua PromptCompressor: {e}")
    raise e

@app.get(
    "/compress",
    summary="Comprime un prompt",
    description="Recibe un prompt a través de una solicitud GET, lo procesa y devuelve una versión comprimida."
)
def compress_prompt(
    prompt: str = Query(..., min_length=1, description="El prompt que deseas comprimir"),
    rate: float = Query(0.5, ge=0.0, le=1.0, description="Tasa de compresión deseada (0.0 - 1.0)")
):
    """
    Endpoint para comprimir un prompt.

    - **prompt**: El texto del prompt que se desea comprimir.
    - **rate**: La tasa de compresión deseada.
    """
    logger.info(f"Recibido prompt para comprimir: {prompt} con tasa de compresión: {rate}")
    try:
        # Llamar al método de compresión de PromptCompressor
        result = compressor.compress_prompt(
            context=[prompt],
            rate=rate
        )
        logger.info(f"Prompt comprimido: {result['compressed_prompt']}")
        return {"compressed_prompt": result["compressed_prompt"]}
    except Exception as e:
        logger.error(f"Error al comprimir el prompt: {e}")
        raise HTTPException(status_code=500, detail="Error al comprimir el prompt.")

# Punto de entrada para ejecutar el servidor
if __name__ == "__main__":
    # Ejecutar el servidor en 0.0.0.0:8000 para estar disponible en la red
    uvicorn.run("bot:app", host="0.0.0.0", port=8000, reload=True)
