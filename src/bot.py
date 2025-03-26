from fastapi import FastAPI, Request
import subprocess
import os
import chardet
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

app = FastAPI()
# Añadir los middlewares
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TimeoutMiddleware, timeout_seconds=30)

# Path to the Llama model and executable
MODEL_PATH = "src/models/tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
LLAMAFILE_EXECUTABLE = "src/llamafile/llamafile.exe"

SYSTEM_PROMPT = """You are a helpful AI assistant. You provide accurate, factual responses.
You respond in the same language that the user uses to ask the question.
If the user says "Hola", you respond in Spanish. If they say "Hello", you respond in English."""

def clean_response(response: str) -> str:
    """Clean up the model response to extract only the assistant's reply."""
    # If the response contains the assistant marker, take everything after it
    if "<|assistant|>" in response:
        response = response.split("<|assistant|>")[-1]
    
    # Remove any other markers that might appear
    markers = ["<|system|>", "<|user|>", "<|assistant|>", SYSTEM_PROMPT]
    for marker in markers:
        response = response.replace(marker, "")
    
    # Remove any user input that might have been echoed
    if ":" in response:
        # Take only the part after the last colon, which is usually the actual response
        parts = response.split(":")
        if len(parts) > 1:
            response = ":".join(parts[1:])
    
    return response.strip()

@app.get("/query")
async def query_model(prompt: str, request: Request):
    """
    Endpoint to query the Llama model.
    :param prompt: The input prompt to send to the model.
    :return: The model's response.
    """
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", "Unknown")
    
    logger.info(f"[{request_id}] Starting model query with prompt: {prompt}")

    if not os.path.exists(LLAMAFILE_EXECUTABLE):
        logger.error(f"[{request_id}] Llamafile executable not found")
        return {"error": "Llamafile executable not found."}

    if not os.path.exists(MODEL_PATH):
        logger.error(f"[{request_id}] Model file not found")
        return {"error": "Model file not found."}

    try:
        # Format the prompt with system prompt and chat formatting
        formatted_prompt = f"<|system|>{SYSTEM_PROMPT}<|user|>{prompt}<|assistant|>"
        
        logger.info(f"[{request_id}] Starting llamafile process")
        model_start_time = time.time()
        
        # Run the Llama model using the executable with optimized parameters
        process = await asyncio.create_subprocess_exec(
            LLAMAFILE_EXECUTABLE,
            "--model", MODEL_PATH,
            "--temp", "0.1",            # Lower temperature for faster, more focused responses
            "--ctx-size", "2048",       # Smaller context window for faster processing
            "--batch-size", "512",      # Smaller batch size for quicker processing
            "--threads", "4",           # Use 4 threads for good balance
            "--top-k", "20",            # Lower top-k for faster sampling
            "--top-p", "0.5",          # Lower top-p for more focused responses
            "-n", "100",               # Limit maximum tokens to generate
            "--repeat-penalty", "1.2",  # Slightly increase repetition penalty
            "--seed", "-1",            # Set a seed for reproducibility
            "-e",                      # Enable prompt escaping
            "-p", formatted_prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            # Wait for the process with timeout
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=25)
            model_time = time.time() - model_start_time
            logger.info(f"[{request_id}] Model processing completed in {model_time:.3f}s")
            
            if process.returncode != 0:
                # Detect encoding of stderr and decode
                detected_encoding = chardet.detect(stderr).get('encoding') or 'utf-8'
                error_message = stderr.decode(detected_encoding)
                logger.error(f"[{request_id}] Model error: {error_message}")
                return {"error": "Error running the model.", "details": error_message}

            # Detect encoding of stdout and decode
            detected_encoding = chardet.detect(stdout).get('encoding') or 'utf-8'
            response_message = stdout.decode(detected_encoding).strip()

            # Clean up and extract only the model's response
            cleaned_response = clean_response(response_message)
            
            total_time = time.time() - start_time
            logger.info(f"[{request_id}] Request completed successfully in {total_time:.3f}s")

            return {
                "response": cleaned_response,
                "metadata": {
                    "processing_time": total_time,
                    "model_time": model_time,
                    "request_id": request_id
                }
            }
            
        except asyncio.TimeoutError:
            # Make sure to terminate the process if it times out
            process.terminate()
            await process.wait()
            logger.error(f"[{request_id}] Request timed out after {time.time() - start_time:.3f}s")
            return {"error": "Request timed out", "details": "The model took too long to respond"}

    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}")
        return {"error": "An exception occurred.", "details": str(e)}

@app.get("/")
def root():
    return {"message": "Welcome to the Llama model API!"}

