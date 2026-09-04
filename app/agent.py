# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime
import json
import os
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google import genai
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.cloud import firestore, storage
from google.genai import types

from app.a2ui_utils import a2ui_callback

MODEL = "gemini-3.6-flash"

# HARDCODED GCP PROJECT ID (Required: Do not use google.auth.default() or GOOGLE_CLOUD_PROJECT)
PROJECT_ID = "qwiklabs-gcp-03-4f265f3b8af7"

# HARDCODED GCS BUCKET NAME (Required: Publicly accessible Cloud Storage bucket)
BUCKET_NAME = "antigravity-it-workout-coach-assets-4f265f3b"



def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


async def generate_memories_callback(callback_context: CallbackContext):
    """Write callback: Send completed session events to Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


def list_workout_tasks(category: str = "", status: str = "") -> str:
    """Lists IT workout tasks from Firestore, with optional category or status filtering.

    Args:
        category: Optional filter by category (e.g., 'Antigravity', 'Agent CLI', 'M365 Copilot').
        status: Optional filter by status (e.g., 'not_started', 'in_progress', 'completed').

    Returns:
        A list or string representation of matching workout tasks.
    """
    db = get_firestore_client()
    query_ref = db.collection("workout_tasks")
    if category:
        query_ref = query_ref.where("category", "==", category)
    if status:
        query_ref = query_ref.where("status", "==", status)

    docs = query_ref.stream()
    tasks = [doc.to_dict() for doc in docs]
    if not tasks:
        return "No workout tasks found matching criteria."
    return str(tasks)


def add_workout_task(
    title: str,
    category: str,
    difficulty: str,
    estimated_minutes: int,
    description: str,
) -> str:
    """Adds a new IT workout task to the Firestore database.

    Args:
        title: Title of the IT workout task.
        category: Category of the task (e.g., 'Antigravity', 'Agent CLI', 'M365 Copilot').
        difficulty: Difficulty level ('Beginner', 'Intermediate', 'Advanced').
        estimated_minutes: Estimated duration in minutes.
        description: Detailed instruction of the task.

    Returns:
        Confirmation message with the created task_id.
    """
    db = get_firestore_client()
    collection_ref = db.collection("workout_tasks")
    task_id = f"task_{int(datetime.datetime.now(datetime.timezone.utc).timestamp())}"
    task_doc = {
        "task_id": task_id,
        "title": title,
        "category": category,
        "difficulty": difficulty,
        "estimated_minutes": estimated_minutes,
        "description": description,
        "status": "not_started",
    }
    collection_ref.document(task_id).set(task_doc)
    return f"Successfully added workout task [{task_id}] '{title}'"


def update_workout_task_status(task_id: str, status: str) -> str:
    """Updates the status of an existing IT workout task in Firestore.

    Args:
        task_id: ID of the task to update (e.g., 'task_001').
        status: New status ('not_started', 'in_progress', 'completed').

    Returns:
        Confirmation message of the status update.
    """
    db = get_firestore_client()
    doc_ref = db.collection("workout_tasks").document(task_id)
    doc = doc_ref.get()
    if not doc.exists:
        return f"Error: Task [{task_id}] not found in database."

    doc_ref.update({"status": status})
    return f"Successfully updated task [{task_id}] status to '{status}'"


DOCS_KNOWLEDGE_BASE = {
    "antigravity": (
        "Google Antigravity allows designing and orchestrating autonomous AI agents with Skills, Rules, and Plugins. "
        "Skills are defined in SKILL.md files with YAML frontmatter containing 'name' and 'description'."
    ),
    "agent cli": (
        "google-agents-cli (agents-cli) provides CLI commands for managing ADK agents: "
        "'agents-cli scaffold' to initialize, 'agents-cli install --clean' to set up .venv, "
        "and 'agents-cli deploy' to deploy to Vertex AI Agent Runtime or Cloud Run."
    ),
    "memory bank": (
        "Vertex AI Memory Bank enables cross-session long-term memory. "
        "Add PreloadMemoryTool to tools and generate_memories_callback to after_agent_callback. "
        "Wire VertexAiMemoryBankService(project=..., location=..., agent_engine_id=...) into the app."
    ),
    "m365 copilot": (
        "M365 Copilot integration allows ADK agents deployed via Agent CLI to communicate over the A2A protocol "
        "and expose agent cards at /.well-known/agent-card.json for Microsoft Copilot plugins."
    ),
    "firestore": (
        "Firestore native mode stores document collections (e.g. workout_tasks). "
        "Initialize firestore.Client(project='YOUR_PROJECT_ID') using a hardcoded string project ID."
    ),
}


def search_antigravity_docs(query: str) -> str:
    """Searches official documentation and references for Google Antigravity, Agent CLI, Memory Bank, and M365 Copilot.

    Args:
        query: The search term or question (e.g., 'agent cli', 'memory bank', 'm365 copilot', 'skill').

    Returns:
        Relevant documentation snippets matching the query.
    """
    query_lower = query.lower()
    matches = []
    for key, content in DOCS_KNOWLEDGE_BASE.items():
        if key in query_lower or any(word in key for word in query_lower.split()):
            matches.append(f"[{key.upper()}]\n{content}")

    if not matches:
        for key, content in DOCS_KNOWLEDGE_BASE.items():
            if any(word in content.lower() for word in query_lower.split() if len(word) > 3):
                matches.append(f"[{key.upper()}]\n{content}")

    if not matches:
        return (
            f"No specific documentation entry found for query '{query}'. "
            f"Covered topics: {', '.join(DOCS_KNOWLEDGE_BASE.keys())}"
        )

    return "\n\n".join(matches)


CORPUS_NAME = "projects/606913921635/locations/us-central1/ragCorpora/845858693294587904"


def consult_gutenberg_corpus(query: str) -> str:
    """Search the Gutenberg literary RAG corpus and return matched passages.

    Args:
        query: What to look up or search for in the Gutenberg corpus documents.

    Returns:
        The matched passages from the corpus, or a note if none found.
    """
    import vertexai
    from vertexai.preview import rag

    try:
        vertexai.init(project=PROJECT_ID, location="us-central1")
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
    except Exception as e:
        return f"Retrieval failed: {e}"

    contexts = getattr(resp.contexts, "contexts", [])
    passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
    return "\n\n---\n\n".join(passages) or "No relevant passage found."


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


def generate_workout_badge_image(
    prompt: str,
    tool_context: ToolContext,
) -> str:
    """Generates an achievement badge image for an IT workout item using gemini-3.1-flash-lite-image,
    saves it to Playground Artifacts, uploads it to Cloud Storage, and returns the public https URL.

    Args:
        prompt: Description of the workout achievement badge or visual item to generate.
        tool_context: ToolContext injected by ADK to save the artifact.

    Returns:
        The public HTTPS URL of the generated image in Cloud Storage.
    """
    client = genai.Client(
        vertexai=True,
        location="global",
        project=PROJECT_ID,
    )

    full_prompt = (
        f"A futuristic glowing 3D vector achievement badge emblem for IT workout: {prompt}. "
        "Sleek metallic gold and neon cyan highlights, dark background, highly detailed."
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=full_prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break
        if image_bytes:
            break

    if not image_bytes:
        return f"Failed to generate image for prompt: '{prompt}'"

    ext = "jpg" if "jpeg" in mime_type or "jpg" in mime_type else "png"
    timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    filename = f"badge_{timestamp}.{ext}"

    # (1) Save artifact in Playground Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # (2) Upload same image bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return f"Successfully generated achievement badge! Public URL: {public_url}"


def generate_workout_teaser_video(
    prompt: str,
    tool_context: ToolContext,
) -> str:
    """Generates a short teaser video for an IT workout item using Google's Omni model (gemini-omni-flash-preview)
    in the global region, saves it to Playground Artifacts, uploads it to Cloud Storage, and returns the public https URL.

    Args:
        prompt: Description of the workout teaser video scene to generate.
        tool_context: ToolContext injected by ADK to save the artifact.

    Returns:
        The public HTTPS URL of the generated video in Cloud Storage.
    """
    client = genai.Client(
        vertexai=True,
        location="global",
        project=PROJECT_ID,
    )

    full_prompt = (
        f"A dynamic 3D motion teaser video for IT workout: {prompt}. "
        "Futuristic neon lines, high energy particle effects, professional 4K tech showcase style."
    )

    interaction = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=full_prompt,
    )

    if not interaction or not getattr(interaction, "output_video", None) or not getattr(interaction.output_video, "data", None):
        return f"Failed to generate video for prompt: '{prompt}'"

    raw_data = interaction.output_video.data
    if isinstance(raw_data, str):
        video_bytes = base64.b64decode(raw_data)
    else:
        video_bytes = raw_data

    timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    filename = f"teaser_{timestamp}.mp4"

    # (1) Save artifact in Playground Artifacts panel
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # (2) Upload same video bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return f"Successfully generated workout teaser video! Public URL: {public_url}"


# Configure Agent Engine Sandbox Code Execution
AGENT_ENGINE_RESOURCE_NAME = "projects/606913921635/locations/us-east1/reasoningEngines/790856723626721280"
_meta_path = os.path.join(os.path.dirname(__file__), "..", "deployment_metadata.json")
if os.path.exists(_meta_path):
    try:
        with open(_meta_path, "r") as _f:
            _meta = json.load(_f)
            AGENT_ENGINE_RESOURCE_NAME = _meta.get("remote_agent_runtime_id", AGENT_ENGINE_RESOURCE_NAME)
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=AGENT_ENGINE_RESOURCE_NAME
)


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are an IT Skill Workout Coach designed to guide learners in mastering "
        "Google Antigravity, Agent CLI, and M365 Copilot."
    ),
    workflow_description=(
        "Analyze the request and return structured UI when appropriate. Use workout_tasks tools "
        "(list_workout_tasks, add_workout_task, update_workout_task_status) to view, "
        "create, and update learning tasks. Use consult_gutenberg_corpus to query "
        "the Gutenberg library corpus. Use generate_workout_badge_image to generate "
        "and publish achievement badges. Use generate_workout_teaser_video to generate "
        "and publish video teasers for workouts. You can safely execute Python code using sandbox code execution. "
        "You remember user preferences across conversations."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    code_executor=code_executor,
    tools=[
        list_workout_tasks,
        add_workout_task,
        update_workout_task_status,
        search_antigravity_docs,
        consult_gutenberg_corpus,
        generate_workout_badge_image,
        generate_workout_teaser_video,
        get_weather,
        get_current_time,
        PreloadMemoryTool(),
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

agent = root_agent







