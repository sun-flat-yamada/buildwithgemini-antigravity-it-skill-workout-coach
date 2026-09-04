# 🏛️ System Prompt, Harness Design, & Setup Architecture Guide

This document provides a comprehensive technical breakdown of the system prompts, environment setup, lab operations harness design, VM initialization, reproducible real datasets, and the **Automated Demo Video Recording Realization Mechanism** for the **IT Skill Workout Coach** agent application.

---

## 1. ⚙️ Antigravity Lab Configuration, Setup & Prompt Overview

### 1. Authentication & Environment Configuration Files

- **`lab.env`** (`/config/automata/lab.env`): Contains Qwiklabs participant credentials (`AG_EMAIL`, `AG_PASSWORD`) and GCP Project ID (`AG_PROJECT_ID`).
- **App `.env`** (`/config/Desktop/BuildWithGemini/antigravity-it-skill-workout-coach/.env`): Vertex AI and GCP project settings:
  ```env
  GOOGLE_GENAI_USE_VERTEXAI=true
  GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-03-4f265f3b8af7
  GOOGLE_CLOUD_LOCATION=global
  MEMORY_BANK_ID=7139003105068187648
  ```

### 2. System Prompts & Requirement Specifications

- **`agent.py (instruction)`**: System instruction for the IT Skill Workout Coach persona and A2UI card formatting directives.
- **`project_brief.md`** (`/config/Desktop/BuildWithGemini/project_brief.md`): Requirement specification detailing core rails (memory, tools, eval, deploy, frontend) and stretch features (A2UI catalog/tables, image gen badges/diagrams, code sandbox progress graphs).
- **`GEMINI.md`** (`/config/Desktop/BuildWithGemini/antigravity-it-skill-workout-coach/GEMINI.md`): AI agent coding guide specifying prerequisites, 6-phase development workflow, CLI commands, and operational constraints (e.g., code preservation, model retention).
- **`SKILL.md (troubleshoot-lab-setup)`** (`/config/Desktop/BuildWithGemini/.agents/skills/troubleshoot-lab-setup/SKILL.md`): Diagnostic prompt verifying GCP login state, IAM permissions (`roles/aiplatform.user`), enabled APIs, and environment readiness.

### 3. Automation Scripts, Interceptors, & Marker Flags

- **`automata/bin/`**:
  - `ag_autologin.py`: Automated login script orchestrating GCP and Antigravity CLI sign-in.
  - Browser interceptors (`xdg-open`, `shim`): Intercepts browser launch calls within the remote desktop environment.
- **`.antigravity-lab-setup-complete`** (`/config/.antigravity-lab-setup-complete`): Marker flag file indicating that the lab environment initialization has successfully completed.

---

## 2. 🤖 Agent System Prompt Architecture

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

## 3. ⚙️ Infrastructure & IAM Configuration

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

## 4. 🧪 Lab Operations Harness Design & Implementation

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

---

## 5. 🎬 Automated Demo Video Realization Mechanism (Detailed Architecture)

The automated demo video recording and presentation pipeline fulfills the core prompt requirement:

> *"Record a demo video of my agent. Show it doing the thing my app does best, then ask a second, richer prompt that shows off a tool call, a database lookup, or a generated image."*

This pipeline operates deterministically through 5 systematic phases:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. Playwright Automation Script (scratch/record_demo.py)                                │
│    ├── Phase A: Launch Chromium with record_video_dir (1280x720 Viewport)                │
│    ├── Phase B: Prompt 1 (Firestore Lookup): "Antigravityカテゴリのタスク一覧"          │
│    │            └── Wait for DOM .a2card render (list_workout_tasks tool call)          │
│    └── Phase C: Prompt 2 (Multimodal Badge Gen): "Antigravityアチーブメントバッジ生成"   │
│                 └── Wait for tool call (gemini-3.1-flash-lite-image -> GCS -> <img>)   │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │ (Raw WebM Video File)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. Pure Python Audio Synthesizer Engine (scratch/generate_lofi_music.py)                 │
│    ├── Harmonic Cmaj7-Am7-Dm7-G7 chord progression via warm sine oscillators & RC filter │
│    ├── 84 BPM Lo-Fi drum pattern (Exponential kick, noise-burst snare, hi-hat)          │
│    └── Vinyl crackle & Poisson impulse noise layer -> Outputs lofi_music.wav            │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │ (20s Stereo WAV Audio)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. FFmpeg Video Transcoding & Multiplexing Engine                                       │
│    ├── Multiplex Audio + Video: demo_lofi.mp4 (H.264/AAC) & demo_lofi.webm (VP9/Opus)    │
│    └── Two-Pass Palette GIF Generator: palettegen/paletteuse @ 15 FPS -> demo.gif       │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │ (Inline Optimized Asset)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. Inline Presentation Layer                                                            │
│    └── Embedded relative link ![Demo](./demo.gif) in README.md top showcase             │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: Headless Browser & Scenario Orchestration (`scratch/record_demo.py`)
- Uses `playwright.async_api` to launch a headless Chromium browser instance with `record_video_dir` enabled at 1280x720 HD resolution.
- Navigates to `http://127.0.0.1:8080` (the custom FastAPI chat frontend).

### Phase 2: Two-Stage Prompt Execution Sequence
1. **Stage 1 (Core Application Functionality & Database Lookup)**:
   - Types: `"Antigravityカテゴリのワークアウトタスク一覧を表示して"`
   - Trigger: Calls `list_workout_tasks` tool on Firestore database.
   - UI Render: Receives A2UI JSON payload and renders a styled `.a2card` component with task titles, status badges, and estimated duration.
   - Pause: 6-second hold for clear visual inspection.
2. **Stage 2 (Richer Multimodal Tool Call & Image Generation)**:
   - Types: `"Antigravityマスター達成のアチーブメントバッジ画像を生成して"`
   - Trigger: Calls `generate_workout_badge_image` tool, invoking `gemini-3.1-flash-lite-image` via Vertex AI.
   - Storage & UI Render: Uploads image bytes to public GCS bucket (`antigravity-it-workout-coach-assets-4f265f3b`) and renders an inline `<img>` within the chat bubble.
   - Pause: 8-second hold for visual badge showcase.

### Phase 3: Pure Python 84 BPM Lo-Fi Audio Synthesizer Engine (`scratch/generate_lofi_music.py`)
To avoid third-party music API dependencies and recurring audio license costs, an 84 BPM Lo-Fi Hip Hop audio track was programmatically synthesized using `numpy` and `scipy.io.wavfile`:
- **Chord Progression**: Cmaj7 - Am7 - Dm7 - G7 synthesized with multi-frequency sine oscillators and low-pass RC filter smoothing.
- **Percussion Synthesizer**:
  - Kick: Exponential sine frequency sweep (120 Hz → 40 Hz).
  - Snare: Filtered white noise with exponential decay envelope.
  - Hi-Hat: High-pass filtered noise bursts placed on eighth-note sub-beats.
- **Analog Vinyl Effect**: Layered Poisson impulse crackle and pink noise.

### Phase 4: FFmpeg Transcoding & Two-Pass Palette GIF Optimization
- **Multiplexing**: Merges recorded video stream and WAV audio using FFmpeg (`-c:v libx264 -c:a aac` for MP4, `-c:v libvpx-vp9 -c:a libopus` for WebM).
- **Two-Pass GIF Optimization**:
  - Pass 1: Generates an optimal 256-color palette (`palettegen`).
  - Pass 2: Applies palette mapping with Bayer dithering (`paletteuse`) at 15 FPS and 800px width.
  - Result: Produces a lightweight, smooth, high-fidelity looping `./demo.gif` (< 3 MB).

### Phase 5: Inline README Integration
- Linked directly near the top of `README.md` using relative path `![Demo](./demo.gif)` for instant, inline looping playback on GitHub.

---

## 6. 📦 Reproducible Real Datasets

### 1. Firestore Tasks Seed Dataset (`docs/seed_data/firestore_tasks.json`)
Contains the initial state of IT workout tasks used by the agent during database lookups.

### 2. Agent Evaluation Dataset (`tests/eval/datasets/workout-coach-dataset.json`)
Contains multi-turn evaluation test cases for validating task listing, badge generation, video teaser creation, and skill guidance.
