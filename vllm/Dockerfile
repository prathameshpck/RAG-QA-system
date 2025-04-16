# Dockerfile (for vllm service)
FROM vllm/vllm-openai:latest

# Create working directory
WORKDIR /app

# Copy code
COPY main.py /app/main.py
COPY ingestion_utils.py /app/ingestion_utils.py

# Install dependencies
RUN pip install weaviate-client sentence_transformers weaviate cryptography cffi protobuf==5.29.0
# Optional: Set NCCL/CUDA env vars (safe defaults)
ENV NCCL_DEBUG=INFO \
    NCCL_BLOCKING_WAIT=1 \
    CUDA_VISIBLE_DEVICES=0 \
    TORCH_NCCL_BLOCKING_WAIT=1

ENTRYPOINT ["python3", "/app/main.py"]
