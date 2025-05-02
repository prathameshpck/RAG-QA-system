# 🎧 LLM-Powered Podcast Q&A Platform

An end-to-end **Retrieval-Augmented Generation (RAG)** system deployed on AWS that enables natural language question answering over a large corpus of podcast transcripts using modern open-source AI infrastructure.

<p align="center">
  <img src="https://img.shields.io/badge/deployment-Docker%20%7C%20Kubernetes-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/monitoring-Prometheus%20%7C%20Grafana-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/inference-vLLM%20%7C%20Gwen%201.5B-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/load%20tested-Locust-critical?style=for-the-badge"/>
</p>

## 🧠 System Overview

This project demonstrates how to integrate cutting-edge components to build a real-world, scalable Q&A platform:

- **Vector DB:** Weaviate stores over **10,000 podcast transcripts**, indexed for semantic similarity.
- **LLM Backend:** vLLM inference using the lightweight **Gwen 1.5B** model, optimized for chat.
- **Frontend UI:** React interface served via NGINX, allowing users to query and receive streaming LLM responses.
- **Observability:** Real-time monitoring of GPU and API metrics via **Prometheus + Grafana**.
- **Deployment:** Fully containerized with **Docker Compose**, scalable via **Kubernetes**.
- **Load Testing:** Simulated realistic concurrent usage with **Locust** to benchmark latency under stress.

## ⚙️ Tech Stack

| Layer          | Tool(s) Used                        |
|---------------|-------------------------------------|
| Inference      | `vLLM`, `Gwen 1.5B` (Quantized)     |
| Retrieval      | `Weaviate`                         |
| Frontend       | `React + NGINX`                    |
| Containerization| `Docker`, `Docker Compose`        |
| Orchestration  | `Kubernetes`                       |
| Monitoring     | `Prometheus`, `Grafana`            |
| Load Testing   | `Locust`                           |
| Deployment     | `AWS EC2` with T4 GPU              |

## 🚀 Key Features

- 🔍 **Retrieval-Augmented QA** using semantically indexed podcast content
- ⚡ **Streaming Chat Interface** powered by SSE-compatible vLLM setup
- 📊 **Metrics Dashboard** tracking token throughput, GPU usage, latency
- 🔄 **K8s-native Scaling** of LLM inference pods
- 🧪 **Load tested** up to 5+ concurrent users per pod with intelligent batching

## 📸 Load Testing Results

<p align="center">
  <img src="assets/load-test.png" width="500"/>
  <br>
  <em>Load Testing results</em>
</p>

## 📈 Sample Metrics

| Metric              | Value                    |
|---------------------|--------------------------|
| Inference Latency   | ~17–25s (1 pod)          |
| Users Supported     | 5 concurrent (scalable)  |
| Tokens/second       | ~30-50 TPS per pod       |
| GPU Type            | `T4` Spot Instance       |

> 💡 With 2 pods, latency improved by ~30% and throughput nearly doubled.

## 🧪 Load Testing Setup

Locust simulates user sessions with 5-message chat prompts using realistic message delays and concurrency. Results integrated into Grafana dashboards with test-time annotation.

## 📦 Project Structure

```bash
.
├── backend/               # FastAPI + vLLM server
├── frontend/              # React + NGINX frontend
├── vector_db/             # Weaviate + Transcript ingestion
├── prometheus/            # Prometheus config
├── grafana/               # Grafana dashboards
├── locust/                # Load testing scripts
├── docker-compose.yaml
└── k8s/                   # Kubernetes manifests
