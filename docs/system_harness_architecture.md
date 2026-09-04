# 🏛️ System Prompt, Harness Design, & Setup Architecture Guide

This document provides a comprehensive technical breakdown of the system prompt, environment setup, lab operations harness design, and reproducible real datasets for the **IT Skill Workout Coach** agent application.

---

## 1. 🤖 System Prompt & Instruction Architecture

The agent's personality, execution constraints, and UI output formats are controlled via layered system prompts defined in [`app/agent.py`](../app/agent.py).

### System Instruction (`a2ui_instruction`)

```text
You are an IT Skill Workout Coach helping users master Google Antigravity, Agent CLI, and M365 Copilot.

CRITICAL A2UI INSTRUCTION:
When responding to user requests, whenever possible, present your structured response as an A2UI card using the A2UI tools/schema provided.
For task lists, skill guides, badges, or videos, output rich A2UI cards instead of long plain text.

Available Tools:
1. list_workout_tasks: Queries Firestore for IT workout tasks.
2. update_workout_task_status: Updates task status in Firestore.
3. generate_workout_badge_image: Generates 3D achievement badges using gemini-3.1-flash-lite-image and publishes to GCS.
4. generate_workout_teaser_video: Generates short 3D motion teaser videos using gemini-omni-flash-preview in global region and publishes to GCS.
```

---

## 2. ⚙️ Environment Setup & Infrastructure Configuration

### Project Configuration (`agents-cli-manifest.yaml`)

```yaml
agent_directory: app
project_id: qwiklabs-gcp-03-4f265f3b8af7
location: us-east1
staging_bucket: gs://qwiklabs-gcp-03-4f265f3b8af7-agent-staging
```

### Granted IAM Roles

- `roles/datastore.user`: Granted to Agent Engine & Cloud Run service accounts for Firestore read/write access.
- `roles/storage.objectAdmin`: Granted to service accounts for public GCS bucket (`antigravity-it-workout-coach-assets-4f265f3b`).
- `roles/aiplatform.user`: Granted to Cloud Run service account to invoke the Vertex AI Reasoning Engine over A2A protocol.

---

## 3. 🧪 Lab Operations Harness Design & Implementation

The lab operations harness connects the browser UI, local development environment, GCP serverless infrastructure, and recording pipelines through 5 specialized layers:

```
[Browser UI (index.html)]
       │ (HTTP POST /chat)
       ▼
[FastAPI Gateway Proxy (main.py)]
       │ (A2A Protocol / StreamQuery)
       ▼
[Agent Platform Runtime (us-east1)] ──► [Firestore / GCS / RAG]
       │
       ▼
[Playwright & Audio Synthesizer] ──► [FFmpeg Video Pipeline] ──► [GIF / MP4]
```

### 1. CLI & Evaluation Harness
- **`google-agents-cli` (`agents-cli`)**: Handles local playground server, unit/integration test runner (`uv run pytest`), and evaluation dataset synthesis (`agents-cli eval`).

### 2. A2A Gateway & FastAPI Proxy Harness (`frontend/main.py`)
- Translates browser REST calls into the **A2A Protocol** (`StreamQuery` / `GenerateStreamResponse`).
- Authenticates using Google Application Default Credentials (`google.auth.default()`).

### 3. A2UI Component Rendering Harness (`frontend/static/index.html`)
- Parses streamed A2UI `surfaceUpdate` JSON blocks.
- Maps flat component schemas (`Card`, `Column`, `Row`, `Text`, `Image`, `Icon`) directly to DOM nodes (`buildNode`, `renderSurface`).

### 4. Data & Artifact Storage Harness
- **Firestore Harness**: Manages IT skill task documents under collection `workout_tasks`.
- **GCS Asset Harness**: Uploads binary byte streams directly to public GCS bucket `antigravity-it-workout-coach-assets-4f265f3b` and returns public HTTPS URLs.

### 5. Automated Video & Audio Recording Harness
- **Headless Playwright (`record_demo.py`)**: Automates browser user interactions on `http://localhost:8080`.
- **SciPy/NumPy Audio Synthesizer (`generate_lofi_music.py`)**: Programmatically generates an 84 BPM Lo-Fi Hip Hop track (Cmaj7 - Am7 - Dm7 - G7) with vinyl crackle.
- **FFmpeg Processing Pipeline**: Multiplexes audio/video streams, converts WebM to MP4, and generates palette-optimized looping GIFs.

---

## 4. 📦 Reproducible Real Datasets

### 1. Firestore Tasks Seed Dataset (`docs/seed_data/firestore_tasks.json`)
Contains the initial state of IT workout tasks used by the agent during database lookups.

### 2. Agent Evaluation Dataset (`tests/eval/datasets/workout-coach-dataset.json`)
Contains multi-turn evaluation test cases for validating task listing, badge generation, video teaser creation, and skill guidance.
