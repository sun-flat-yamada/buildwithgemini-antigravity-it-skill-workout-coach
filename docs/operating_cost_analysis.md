# 📊 Operating Cost Analysis & Budget Guide

This document provides an exhaustive technical and financial cost breakdown for operating the **IT Skill Workout Coach** agent application across Google Cloud Platform (GCP) and associated services.

---

## 1. 🏗️ Service-by-Service Pricing Breakdown

### 1. Vertex AI Generative Models (LLM Inference & Multimodal)

| Component / Model | Operation | Unit Cost Rate (USD) | Usage Pattern |
| --- | --- | --- | --- |
| **`gemini-3.6-flash`** | Text & Function Calling (Input) | **$0.075** / 1M tokens | Prompts, conversation history, tool outputs (~4,000 tokens/turn) |
| **`gemini-3.6-flash`** | Text & Function Calling (Output) | **$0.30** / 1M tokens | Agent reasoning & A2UI card payloads (~500 tokens/turn) |
| **`gemini-3.1-flash-lite-image`** | 3D Achievement Badge Generation | **$0.0005** / image | Invoked on `generate_workout_badge_image` |
| **`gemini-omni-flash-preview`** | 3D Teaser Video Generation | **$0.05** / video | Invoked on `generate_workout_teaser_video` |

---

### 2. Vertex AI Agent Platform & Memory Services

| Service | Operation | Unit Cost Rate (USD) | Description |
| --- | --- | --- | --- |
| **Vertex AI Reasoning Engine** | Managed Agent Runtime | **$0.00** base runtime fee | Charged based on underlying LLM inference API calls |
| **Vertex AI Memory Bank** | Memory Extraction Callback | **$0.075** / 1M tokens | Asynchronous extraction of user preferences & workout history |

---

### 3. Vertex AI RAG Engine & Embedding Search

| Component | Operation | Unit Cost Rate (USD) | Description |
| --- | --- | --- | --- |
| **`text-embedding-005`** | Document Vector Embedding | **$0.025** / 1M tokens | One-time ingestion for Gutenberg & Antigravity docs |
| **RAG Managed DB (Serverless)** | Storage | **$0.10** / GB / month | Vector index storage for literature & tech docs |
| **RAG Retrieval Query** | Vector Similarity Search | **$0.00** / query | Search compute included in serverless mode |

---

### 4. Cloud Database & Asset Storage

| Cloud Service | Resource | Unit Cost Rate (USD) | Notes |
| --- | --- | --- | --- |
| **Cloud Firestore (Native Mode)** | Document Reads | **$0.06** / 100k reads | `list_workout_tasks` & query lookups |
| **Cloud Firestore (Native Mode)** | Document Writes | **$0.18** / 100k writes | `add_workout_task` & `update_workout_task_status` |
| **Cloud Firestore (Native Mode)** | Document Storage | **$0.18** / GB / month | First 1 GiB free per project |
| **Cloud Storage (GCS Standard)** | Asset Bucket Storage | **$0.02** / GB / month | Badge images (`.jpg`/`.png`) and video teasers (`.mp4`) |
| **Cloud Storage (GCS Standard)** | Class A Operations (Upload) | **$0.05** / 10k ops | Uploading generated image/video byte streams |
| **Cloud Storage (GCS Standard)** | Class B Operations (Download) | **$0.004** / 10k ops | Serving public asset URLs to browser clients |

---

### 5. Serverless Compute & Network Egress

| Service | Metric | Free Tier Allowance | Pay-As-You-Go Rate |
| --- | --- | --- | --- |
| **Cloud Run (FastAPI Proxy)** | vCPU Second | 180,000 vCPU-sec / month | **$0.00002400** / vCPU-sec |
| **Cloud Run (FastAPI Proxy)** | Memory Second | 360,000 GiB-sec / month | **$0.00000250** / GiB-sec |
| **Cloud Run (FastAPI Proxy)** | Requests | 2M requests / month | **$0.40** / 1M requests |
| **Internet Egress** | Data Transfer | 100 GB / month | **$0.08 – $0.12** / GB |

---

## 2. 📈 Operational Cost Scenarios & Projections

Below are 3 realistic operational scale models based on monthly user activity.

### Scenario A: Personal / Workshop Trial Scale
- **Monthly Turn Volume**: 1,000 user turns
- **Badge Generations**: 20 images
- **Video Teaser Generations**: 5 videos
- **Estimated Monthly Cost**: **~$0.45 – $1.20 / month** (Covered almost entirely by GCP Free Tier)

### Scenario B: Team / Departmental Scale
- **Monthly Turn Volume**: 50,000 user turns
- **Badge Generations**: 1,000 images
- **Video Teaser Generations**: 200 videos
- **Estimated Monthly Cost**: **~$18.50 – $32.00 / month**

### Scenario C: Enterprise Scale
- **Monthly Turn Volume**: 500,000 user turns
- **Badge Generations**: 10,000 images
- **Video Teaser Generations**: 2,000 videos
- **Estimated Monthly Cost**: **~$280.00 – $450.00 / month**

---

## 3. 🛡️ Cost Control & Budget Governance Guidelines

1. **GCP Budget Alerts**: Set up a GCP Budget Alert in the Console at $10.00 / $50.00 / $100.00 thresholds with email notifications.
2. **GCS Lifecycle Rules**: Configure a 30-day auto-deletion lifecycle rule on `antigravity-it-workout-coach-assets-4f265f3b` for temporary video teasers.
3. **Cloud Run Concurrency**: Set `concurrency = 80` and `min_instances = 0` to prevent idle container billing.
