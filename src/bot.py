from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import subprocess
import os
import chardet
import json
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
import asyncio
import time
import logging
from datetime import datetime

# Configurar el logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Registrar inicio de la petición
        start_time = time.time()
        request_id = f"REQ-{int(start_time * 1000)}"
        
        # Log la petición entrante
        logger.info(f"[{request_id}] Request started - Method: {request.method} Path: {request.url.path} Query: {request.query_params}")
        
        try:
            # Procesar la petición
            response = await call_next(request)
            
            # Calcular tiempo de proceso
            process_time = time.time() - start_time
            
            # Log la respuesta
            logger.info(f"[{request_id}] Request completed - Status: {response.status_code} Time: {process_time:.3f}s")
            
            # Añadir headers con información de tiempo de proceso
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log error si ocurre
            logger.error(f"[{request_id}] Request failed - Error: {str(e)}")
            raise e

class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout_seconds=30):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            start_time = time.time()
            return await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            process_time = time.time() - start_time
            logger.error(f"Request timeout after {process_time:.3f}s")
            return JSONResponse(
                status_code=504,
                content={
                    "error": "Request timeout",
                    "detail": f"Request exceeded {self.timeout_seconds} seconds"
                }
            )

# Path to the Llama model and executable
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models/tinyllama-1.1b-chat-v1.0.Q2_K.gguf")
LLAMAFILE_EXECUTABLE = os.path.join(os.path.dirname(__file__), "llamafile/llamafile.exe")
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "models/setting.json")

# Load system prompt from file
PROMPT_PATH = os.path.join(os.path.dirname(__file__), "models/prompt.txt")
with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

# Load model settings
with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
    SETTINGS = json.load(f)
    MODEL_SETTINGS = SETTINGS['model_params']
    CHAT_FORMAT = SETTINGS['chat_format']

def clean_response(response: str) -> str:
    """Clean up the model response to extract only the assistant's reply."""
    # If the response contains the assistant marker, take everything after it
    if CHAT_FORMAT['assistant_prefix'] in response:
        response = response.split(CHAT_FORMAT['assistant_prefix'])[-1]
    
    # Remove any other markers that might appear
    markers = [
        CHAT_FORMAT['system_prefix'], 
        CHAT_FORMAT['user_prefix'], 
        CHAT_FORMAT['assistant_prefix'],
        SYSTEM_PROMPT
    ]
    for marker in markers:
        response = response.replace(marker, "")
    
    # Remove any suffixes
    if CHAT_FORMAT['assistant_suffix']:
        response = response.split(CHAT_FORMAT['assistant_suffix'])[0]
    
    return response.strip()

class LlamaModel:
    def __init__(self):
        self.process = None
        self.lock = asyncio.Lock()

    async def start(self):
        """Inicializa el proceso del modelo."""
        if not os.path.exists(LLAMAFILE_EXECUTABLE):
            raise FileNotFoundError("Llamafile executable not found.")
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Model file not found.")

        logger.info("Starting Llama model process...")
        self.process = None  # Reset process state
        self.process = {
            'executable': LLAMAFILE_EXECUTABLE,
            'model_path': MODEL_PATH,
            'system_prompt': SYSTEM_PROMPT
        }
        logger.info("Llama model initialized successfully")

    async def query(self, prompt: str) -> str:
        """Envía una consulta al modelo."""
        if not self.process:
            raise RuntimeError("Model process not initialized")

        async with self.lock:  # Ensure thread safety
            try:
                # Format prompt using chat format
                formatted_prompt = (
                    f"{CHAT_FORMAT['system_prefix']}{self.process['system_prompt']}{CHAT_FORMAT['system_suffix']}"
                    f"{CHAT_FORMAT['user_prefix']}{prompt}{CHAT_FORMAT['user_suffix']}"
                    f"{CHAT_FORMAT['assistant_prefix']}"
                )
                
                process = await asyncio.create_subprocess_exec(
                    self.process['executable'],
                    "-m", self.process['model_path'],
                    "--temp", MODEL_SETTINGS['temp'],
                    "-n", MODEL_SETTINGS['n_predict'],
                    "-p", formatted_prompt,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    error_message = stderr.decode('utf-8', errors='ignore')
                    logger.error(f"Model error: {error_message}")
                    raise RuntimeError(f"Model error: {error_message}")

                response = stdout.decode('utf-8', errors='ignore')
                return clean_response(response)

            except Exception as e:
                logger.error(f"Error during model query: {str(e)}")
                raise

    async def stop(self):
        """Detiene el proceso del modelo."""
        if self.process:
            self.process = None
            logger.info("Llama model stopped")

# Instancia global del modelo
llama_model = LlamaModel()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await llama_model.start()
    yield
    # Shutdown
    await llama_model.stop()

app = FastAPI(lifespan=lifespan)

# Añadir los middlewares
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TimeoutMiddleware, timeout_seconds=30)

@app.post("/query")
async def query_model(request: Request):
    # Extraer el prompt del cuerpo de la petición
    body = await request.json()
    prompt = body.get("prompt")
    if not prompt:
        return {"error": "No prompt provided"}
    """
    Endpoint to query the Llama model.
    :param prompt: The input prompt to send to the model.
    :return: The model's response.
    """
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", "Unknown")
    
    logger.info(f"[{request_id}] Starting model query with prompt: {prompt}")

    try:
        model_start_time = time.time()
        response = await llama_model.query(prompt)
        model_time = time.time() - model_start_time
        
        total_time = time.time() - start_time
        logger.info(f"[{request_id}] Request completed successfully in {total_time:.3f}s")

        return {
            "response": response,
            "metadata": {
                "processing_time": total_time,
                "model_time": model_time,
                "request_id": request_id
            }
        }

    except Exception as e:
        logger.error(f"[{request_id}] Error: {str(e)}")
        return {"error": "An error occurred", "details": str(e)}

@app.get("/")
def root():
    return {"message": "Welcome to the Llama model API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
