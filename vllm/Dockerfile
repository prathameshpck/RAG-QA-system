# Use vLLM base image
FROM vllm/vllm-openai:latest

# Copy your custom server script into the container
COPY main.py /app/main.py
ENV NCCL_DEBUG=INFO
ENV NCCL_BLOCKING_WAIT=1
ENV CUDA_VISIBLE_DEVICES=0
ENV TORCH_NCCL_BLOCKING_WAIT=1


# Set the default command to run your custom script
ENTRYPOINT ["python3", "/app/main.py"]
