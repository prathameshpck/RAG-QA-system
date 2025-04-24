import os
import json
import time
import asyncio
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Dict
from vllm import LLM
from vllm.sampling_params import SamplingParams
from ingestion_utils import connect_weaviate, query_similar_chunks
from sentence_transformers import SentenceTransformer
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Init app
app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load LLM model
model_name = os.getenv("MODEL_NAME", "neuralmagic/Llama-2-7b-chat-quantized.w8a8")
try:
    engine = LLM(
        model=model_name,
        dtype="half",
        gpu_memory_utilization=0.9,
        enforce_eager=False,
        max_model_len=4096
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

# Prometheus metrics
REQUEST_COUNT = Counter("llm_requests_total", "Total LLM completion requests")
REQUEST_DURATION = Histogram("llm_request_duration_seconds", "LLM request latency (s)")

# Request schema
class ChatRequest(BaseModel):
    model: Optional[str] = None
    messages: List[Dict[str, str]]

# SSE Chat Completions
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    REQUEST_COUNT.inc()
    start_time = time.time()

    try:
        prompt = [m["content"] for m in request.messages if m["role"] == "user"][-1]
        history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in request.messages[:-1]])

        similar_chunks = query_similar_chunks(collection, embedder, prompt, k=2)
        chunks = getattr(similar_chunks, "objects", similar_chunks)
        rag_context = "\n".join([c.properties["content"] for c in chunks])

        system_prompt = "You are a helpful assistant."
        for m in request.messages:
            if m["role"] == "system":
                system_prompt = m["content"]
                break

        full_prompt = f"{system_prompt}\n\nContext:\n{rag_context}\n\nConversation History:\n{history}\n\nUser: {prompt}\nAssistant:"

        # Streaming SamplingParams
        sampling_params = SamplingParams(
            max_tokens=512,
            temperature=0.7,
            top_p=0.9,
            stop=["\nUser:"],
        )

        def format_sse(data):
            return f"data: {json.dumps(data)}\n\n"

        async def event_generator():
            outputs = engine.generate([full_prompt], sampling_params=sampling_params)
            output = outputs[0]
            for char in output.outputs[0].text:
                payload = {
                    "choices": [{
                        "delta": {"content": char},
                        "index": 0,
                        "finish_reason": None
                    }]
                }
                yield format_sse(payload)
                await asyncio.sleep(0)

            yield "data: [DONE]\n\n"

        duration = time.time() - start_time
        REQUEST_DURATION.observe(duration)

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        print(f"Streaming error: {e}")
        return StreamingResponse(
            iter([f"data: {{\"error\": \"{str(e)}\"}}\n\n"]),
            media_type="text/event-stream"
        )

# Prometheus /metrics endpoint
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
