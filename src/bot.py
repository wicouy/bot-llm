from fastapi import FastAPI
import subprocess
import os
import chardet
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
import asyncio
import time

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
            return JSONResponse(
                status_code=504,
                content={
                    "error": "Request timeout",
                    "detail": f"Request exceeded {self.timeout_seconds} seconds"
                }
            )

app = FastAPI()
app.add_middleware(TimeoutMiddleware, timeout_seconds=30)

# Path to the Llama model and executable
MODEL_PATH = "src/models/tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
LLAMAFILE_EXECUTABLE = "src/llamafile/llamafile.exe"

SYSTEM_PROMPT = """You are a helpful AI assistant. You provide accurate, factual responses.
You respond in the same language that the user uses to ask the question.
If the user says "Hola", you respond in Spanish. If they say "Hello", you respond in SPANISH EVER."""

@app.get("/query")
async def query_model(prompt: str):
    """
    Endpoint to query the Llama model.
    :param prompt: The input prompt to send to the model.
    :return: The model's response.
    """
    if not os.path.exists(LLAMAFILE_EXECUTABLE):
        return {"error": "Llamafile executable not found."}

    if not os.path.exists(MODEL_PATH):
        return {"error": "Model file not found."}

    try:
        # Format the prompt with system prompt and chat formatting
        formatted_prompt = f"<|system|>{SYSTEM_PROMPT}<|user|>{prompt}<|assistant|>"
        
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
            "-e",                      # Enable prompt escaping
            "-p", formatted_prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            # Wait for the process with timeout
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=25)
            
            if process.returncode != 0:
                # Detect encoding of stderr and decode
                detected_encoding = chardet.detect(stderr).get('encoding') or 'utf-8'
                error_message = stderr.decode(detected_encoding)
                return {"error": "Error running the model.", "details": error_message}

            # Detect encoding of stdout and decode
            detected_encoding = chardet.detect(stdout).get('encoding') or 'utf-8'
            response_message = stdout.decode(detected_encoding).strip()

            # Clean up the response by removing any remaining tokens
            response_message = response_message.replace("<|assistant|>", "").replace("<|user|>", "").replace("<|system|>", "").strip()

            return {"response": response_message}
            
        except asyncio.TimeoutError:
            # Make sure to terminate the process if it times out
            process.terminate()
            await process.wait()
            return {"error": "Request timed out", "details": "The model took too long to respond"}

    except Exception as e:
        return {"error": "An exception occurred.", "details": str(e)}

@app.get("/")
def root():
    return {"message": "Welcome to the Llama model API!"}

