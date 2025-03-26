import os 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vllm import LLM

# Retrieve model from environment variable or default to a specific model
model_name = os.getenv("MODEL_NAME", "neuralmagic/Llama-2-7b-chat-quantized.w8a8")


# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Optional: Expose additional headers to the browser
)

# Load the LLM model
model_name = "neuralmagic/Llama-2-7b-chat-quantized.w8a8"
try:
    engine = LLM(model=model_name)
    print(f"Model {model_name} loaded successfully.")
except Exception as e:
    print(f"Error loading model {model_name}: {e}")
    raise e

# Endpoint to generate completions
@app.post("/v1/chat/completions")
async def chat_completions(prompt: str):
    try:
        # Generate completions using vLLM
        outputs = engine.generate([prompt])
        return {"completions": outputs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

