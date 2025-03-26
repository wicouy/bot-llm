from fastapi import FastAPI
import subprocess
import os

app = FastAPI()

# Path to the Llama model and executable
MODEL_PATH = "src/models/tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
LLAMAFILE_EXECUTABLE = "src/llamafile/llamafile.exe"

@app.get("/query")
def query_model(prompt: str):
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
        # Run the Llama model using the executable
        result = subprocess.run(
            [LLAMAFILE_EXECUTABLE, "--model", MODEL_PATH, "--prompt", prompt],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {"error": "Error running the model.", "details": result.stderr}

        return {"response": result.stdout.strip()}

    except Exception as e:
        return {"error": "An exception occurred.", "details": str(e)}

@app.get("/")
def root():
    return {"message": "Welcome to the Llama model API!"}

