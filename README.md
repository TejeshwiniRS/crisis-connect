# 🌐 Crisis Connect — Agentic RAG NIM EKS
Agentic RAG system using NVIDIA NIMs (LLM + Embedding) deployed on AWS EKS.

**Crisis Connect** is an **Agentic Retrieval-Augmented Generation (RAG)** system powered by **NVIDIA NIM microservices** and deployed on **AWS EKS**.

It combines:
- **Nemotron LLM NIM** (`llama-3.1-nemotron-nano-8b-v1`) for reasoning  
- **Embedding NIM** for document retrieval  
- A **FastAPI agent** that orchestrates the end-to-end RAG workflow

---

## ⚙️ Architecture

![architecture](docs/architecture.png)

| Component | Description |
|------------|-------------|
| **LLM NIM** | Handles reasoning and text generation |
| **Embedding NIM** | Encodes and retrieves document embeddings |
| **FastAPI Agent** | Performs RAG logic and exposes REST endpoints |
| **AWS EKS** | Hosts all microservices with GPU acceleration |

---

## 🧩 Key Features
- Agentic RAG pipeline on Kubernetes (EKS)
- GPU-accelerated inference with NIM microservices
- `/ingest` and `/ask` endpoints via FastAPI
- Modular and scalable cloud deployment

---

## 🚀 Quick Start

```bash
# Deploy all components
kubectl apply -f k8s/embedding-nim.yaml
kubectl apply -f k8s/llm-nim.yaml
kubectl apply -f k8s/agent.yaml

# Port-forward to access
kubectl -n agentic port-forward svc/agent 8081:8081

# Test the API
curl -F "file=@docs/sample.txt" http://localhost:8081/ingest
curl -X POST http://localhost:8081/ask -H "Content-Type: application/json" -d '{"query":"Summarize the context"}'
