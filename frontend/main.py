"""Minimal FastAPI proxy for a deployed A2A agent (Agent Runtime, agents-cli 1.1.0+).

The browser talks ONLY to this proxy (same origin, no CORS, no GCP creds in the
browser). The proxy authenticates with Application Default Credentials and
forwards chat to the deployed agent over the A2A protocol, returning replies as
structured parts the chat UI knows how to show:

  * {"kind": "text", "text": ...}  -> a normal chat bubble
  * {"kind": "a2ui", "data": ...}  -> one A2UI message (beginRendering /
    surfaceUpdate); static/index.html renders these as a card.
"""

import json
import os
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from google.protobuf.json_format import MessageToDict
import a2a.client as a2a_client
from a2a.types import (
    Message,
    Part,
    Role,
    SendMessageRequest,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

RESOURCE = os.environ["AGENT_ENGINE_RESOURCE_NAME"]
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
_A2UI_MIME = "application/json+a2ui"

_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }


app = FastAPI()


@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


_contexts: dict[str, str] = {}


def _extract_parts_from_dict(parts: list) -> list[dict]:
    out: list[dict] = []
    for p in parts:
        if not isinstance(p, dict):
            continue
        text = p.get("text")
        if text:
            out.append({"kind": "text", "text": text})
            continue

        data = p.get("data")
        meta = p.get("metadata") or {}
        mime = meta.get("mimeType") if isinstance(meta, dict) else None

        if data:
            if mime == _A2UI_MIME or (isinstance(data, (dict, list))) or (isinstance(data, str) and ("beginRendering" in data or "surfaceUpdate" in data)):
                out.append({"kind": "a2ui", "data": data})
            elif isinstance(data, str):
                out.append({"kind": "text", "text": data})

        url = p.get("url")
        if url:
            out.append({"kind": "text", "text": url})
    return out


@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    parts: list[dict] = []

    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        client_config = a2a_client.ClientConfig(httpx_client=client)
        client_instance = await a2a_client.create_client(A2A_BASE, client_config)

        context_id = _contexts.get(user_id)
        msg_kwargs = {
            "message_id": str(uuid.uuid4()),
            "role": Role.ROLE_USER,
            "parts": [Part(text=message)],
        }
        if context_id:
            msg_kwargs["context_id"] = context_id

        msg = Message(**msg_kwargs)
        send_req = SendMessageRequest(message=msg)

        async for event in client_instance.send_message(send_req):
            if hasattr(event, "HasField"):
                if event.HasField("status_update"):
                    su = event.status_update
                    if getattr(su, "context_id", None):
                        _contexts[user_id] = su.context_id
                if event.HasField("task"):
                    task = event.task
                    if getattr(task, "context_id", None):
                        _contexts[user_id] = task.context_id
                    if getattr(task, "artifacts", None):
                        for art in task.artifacts:
                            art_dict = MessageToDict(art)
                            parts.extend(_extract_parts_from_dict(art_dict.get("parts", [])))
                if event.HasField("artifact_update"):
                    art = event.artifact_update.artifact
                    art_dict = MessageToDict(art)
                    parts.extend(_extract_parts_from_dict(art_dict.get("parts", [])))

    if not parts:
        parts = [{"kind": "text", "text": "(The agent didn't return a reply.)"}]
    return JSONResponse({"parts": parts})


# Serve the chat UI
static_dir = "frontend/static" if os.path.exists("frontend/static") else "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
