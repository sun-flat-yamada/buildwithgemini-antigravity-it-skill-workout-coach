# 📊 Operating Cost Analysis & Budget Guide

This document provides an exhaustive technical and financial cost breakdown for operating the **IT Skill Workout Coach** agent application across Google Cloud Platform (GCP) and associated services, including itemized monthly calculations and **Grand Total Estimated Monthly Costs**.

---

## 1. 🏗️ Service & Unit Price Catalog

| Category | Service / Model | Role / Purpose | Unit Rate (USD) | Monthly GCP Free Tier |
| --- | --- | --- | --- | --- |
| **LLM Inference** | **`gemini-3.6-flash`** (Input) | Prompts, context, tool output | **$0.075** / 1M tokens | - |
| **LLM Inference** | **`gemini-3.6-flash`** (Output) | Agent reasoning & A2UI cards | **$0.30** / 1M tokens | - |
| **Image Gen** | **`gemini-3.1-flash-lite-image`** | 3D achievement badges | **$0.0005** / image | - |
| **Video Gen** | **`gemini-omni-flash-preview`** | 3D workout teaser videos | **$0.05** / video | - |
| **Agent Base** | **Vertex AI Reasoning Engine** | Agent Runtime hosting | **$0.00** base runtime fee | - |
| **Memory** | **Vertex AI Memory Bank** | Asynchronous memory extraction | **$0.075** / 1M tokens | - |
| **RAG Search** | **Vertex AI RAG Engine** | Gutenberg & technical docs | **$0.10** / GB / mo (storage) | 1,000 queries/mo free |
| **Database** | **Cloud Firestore (Native)** | Task CRUD operations | Reads: **$0.06** / 100k<br>Writes: **$0.18** / 100k | 1 GiB free / 50k reads/day |
| **Storage** | **Cloud Storage (GCS Standard)** | Public badge & video hosting | **$0.02** / GB / mo | 5 GB free / 100 GB egress |
| **Frontend** | **Cloud Run (FastAPI Proxy)** | Browser-to-Agent A2A Proxy | vCPU: **$0.00002400** / sec<br>req: **$0.40** / 1M reqs | 180k vCPU-sec / 2M reqs |

---

## 2. 💰 Monthly Cost Calculations & Grand Total Estimates

### 🟢 1. Small Scale / Individual & Workshop Use (1,000 Conversation Turns / Month)

*Assumption: 1,000 turns/mo, 20 badge images/mo, 5 video teasers/mo, 100 memory extraction sessions/mo*

| Service Name | Estimated Usage | Formula | Estimated Monthly Cost (USD) |
| --- | --- | --- | --- |
| **Gemini 3.6 Flash (Input)** | 4.0M tokens | 4.0M × $0.075 | $0.30 |
| **Gemini 3.6 Flash (Output)** | 0.5M tokens | 0.5M × $0.30 | $0.15 |
| **Gemini 3.1 Flash Lite Image** | 20 images | 20 × $0.0005 | $0.01 |
| **Gemini Omni Flash (Video)** | 5 videos | 5 × $0.05 | $0.25 |
| **Vertex AI Memory Bank** | 0.2M tokens | 0.2M × $0.075 | $0.015 |
| **Vertex AI RAG Engine** | 0.1 GB | 0.1GB × $0.10 | $0.01 |
| **Cloud Firestore** | < 5,000 ops | Covered by Free Tier ($0.00) | $0.00 |
| **Cloud Storage** | < 1 GB | 1GB × $0.02 | $0.02 |
| **Cloud Run** | < 1,000 reqs | Covered by Free Tier ($0.00) | $0.00 |
| **【GRAND TOTAL ESTIMATED COST】** | - | - | **~$0.755 / month** |

---

### 🟡 2. Medium Scale / Team & Department Use (50,000 Conversation Turns / Month)

*Assumption: 50,000 turns/mo, 1,000 badge images/mo, 200 video teasers/mo, 5,000 memory extraction sessions/mo*

| Service Name | Estimated Usage | Formula | Estimated Monthly Cost (USD) |
| --- | --- | --- | --- |
| **Gemini 3.6 Flash (Input)** | 200M tokens | 200M × $0.075 | $15.00 |
| **Gemini 3.6 Flash (Output)** | 25M tokens | 25M × $0.30 | $7.50 |
| **Gemini 3.1 Flash Lite Image** | 1,000 images | 1,000 × $0.0005 | $0.50 |
| **Gemini Omni Flash (Video)** | 200 videos | 200 × $0.05 | $10.00 |
| **Vertex AI Memory Bank** | 10M tokens | 10M × $0.075 | $0.75 |
| **Vertex AI RAG Engine** | 0.5 GB | 0.5GB × $0.10 | $0.05 |
| **Cloud Firestore** | 100k reads / 20k writes | ($0.06) + ($0.036) | $0.10 |
| **Cloud Storage** | 5 GB | 5GB × $0.02 | $0.10 |
| **Cloud Run** | 50,000 reqs | Covered by Free Tier ($0.00) | $0.00 |
| **【GRAND TOTAL ESTIMATED COST】** | - | - | **~$34.00 / month** |

---

### 🔴 3. Enterprise Scale (500,000 Conversation Turns / Month)

*Assumption: 500,000 turns/mo, 10,000 badge images/mo, 2,000 video teasers/mo, 50,000 memory extraction sessions/mo*

| Service Name | Estimated Usage | Formula | Estimated Monthly Cost (USD) |
| --- | --- | --- | --- |
| **Gemini 3.6 Flash (Input)** | 2,000M tokens | 2,000M × $0.075 | $150.00 |
| **Gemini 3.6 Flash (Output)** | 250M tokens | 250M × $0.30 | $75.00 |
| **Gemini 3.1 Flash Lite Image** | 10,000 images | 10,000 × $0.0005 | $5.00 |
| **Gemini Omni Flash (Video)** | 2,000 videos | 2,000 × $0.05 | $100.00 |
| **Vertex AI Memory Bank** | 100M tokens | 100M × $0.075 | $7.50 |
| **Vertex AI RAG Engine** | 2.0 GB | 2.0GB × $0.10 | $0.20 |
| **Cloud Firestore** | 1M reads / 200k writes | ($0.60) + ($0.36) | $0.96 |
| **Cloud Storage** | 50 GB | 50GB × $0.02 | $1.00 |
| **Cloud Run** | 500k reqs | Covered by Free Tier ($0.00) | $0.00 |
| **Internet Egress** | ~20 GB | Covered by Free Tier (100 GB/mo) | $0.00 |
| **【GRAND TOTAL ESTIMATED COST】** | - | - | **~$339.66 / month** |

---

## 3. 🛡️ Budget Governance Best Practices

1. **Set GCP Budget Alerts**: Configure GCP Billing alerts at $10.00 / $50.00 / $100.00 thresholds.
2. **GCS Lifecycle Policy**: Set a 30-day auto-deletion policy on `antigravity-it-workout-coach-assets-4f265f3b` to clean up old generated videos.
3. **Cloud Run Cold Scale**: Keep `min_instances = 0` to maintain zero billing when no requests arrive.
