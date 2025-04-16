# import os 
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from vllm import LLM

# # Retrieve model from environment variable or default to a specific model
# model_name = os.getenv("MODEL_NAME", "neuralmagic/Llama-2-7b-chat-quantized.w8a8")


# # Initialize FastAPI app
# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["*"],  # Optional: Expose additional headers to the browser
# )

# # Load the LLM model
# model_name = "neuralmagic/Llama-2-7b-chat-quantized.w8a8"
# try:
#     engine = LLM(model=model_name)
#     print(f"Model {model_name} loaded successfully.")
# except Exception as e:
#     print(f"Error loading model {model_name}: {e}")
#     raise e

# # Endpoint to generate completions
# @app.post("/v1/chat/completions")
# async def chat_completions(prompt: str):
#     try:
#         # Generate completions using vLLM
#         outputs = engine.generate([prompt])
#         return {"completions": outputs}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

import os
from vllm.sampling_params import SamplingParams
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from vllm import LLM
from ingestion_utils import connect_weaviate, query_similar_chunks
from sentence_transformers import SentenceTransformer
import traceback
# Initialize FastAPI app
app = FastAPI()
sampling_params = SamplingParams(
    max_tokens=512,
    temperature=0.7,
    top_p=0.9,
    stop=["\nUser:"]
)
# outputs = engine.generate([full_prompt], sampling_params=sampling_params)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load the LLM model with OpenAI server defaults
model_name = os.getenv("MODEL_NAME", "neuralmagic/Llama-2-7b-chat-quantized.w8a8")
try:
    engine = LLM(
        model=model_name,
        dtype="half",                      # auto-detected as float16
        gpu_memory_utilization=0.9,       # OpenAI server default
        enforce_eager=False,              # Allows CUDA graph optimizations
        max_model_len=4096,               # Default OpenAI server value
    )
    print(f"Model {model_name} loaded successfully.")
except Exception as e:
    print(f"Error loading model {model_name}: {e}")
    raise e

# Connect to Weaviate
try:
    weaviate_client = connect_weaviate()
    collection = weaviate_client.collections.get("Huberman_Lab")
    print("Connected to Weaviate.")
    embedder = SentenceTransformer("all-MiniLM-L6-v2") 
except Exception as e:
    print(f"Failed to connect to Weaviate: {e}")
    raise e

# Request schema
class ChatRequest(BaseModel):
    model: Optional[str] = None
    messages: List[Dict[str, str]]

# Endpoint to generate completions

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        # Extract prompt (last user message)
        prompt = [m["content"] for m in request.messages if m["role"] == "user"][-1]

        # Extract chat history (everything except final user message)
        history_context = "\n".join([
            f"{m['role'].capitalize()}: {m['content']}"
            for m in request.messages[:-1]
        ])

        # Query Weaviate for similar chunks
        # similar_chunks = query_similar_chunks(collection, embedder, prompt, k=5)
        # rag_context = "\n".join([chunk["content"] for chunk in similar_chunks])
        # print(rag_context)

        similar_chunks = query_similar_chunks(collection, embedder, prompt, k=2)
        if hasattr(similar_chunks, "objects"):
            chunks_data = similar_chunks.objects
        else:
            chunks_data = similar_chunks

        rag_context = "\n".join([chunk.properties["content"] for chunk in chunks_data])

        # System prompt fallback
        system_prompt = "You are a helpful assistant.Use the context only if it is useful. Answer in grammatically correct english"
        for m in request.messages:
            if m["role"] == "system":
                system_prompt = m["content"]
                break

        # Build the final prompt
        full_prompt = f"{system_prompt}\n\nContext:\n{rag_context}\n\nConversation History:\n{history_context}\n\nUser: {prompt}\nAssistant:"
      
        # Generate completions using vLLM
        outputs = engine.generate([full_prompt] , sampling_params= sampling_params)
        completion_text = outputs[0].outputs[0].text.strip()
        print(outputs, history_context)
        return {"choices": [{"message": {"content": completion_text}}]}
       
    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}, {traceback.format_exc()}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
