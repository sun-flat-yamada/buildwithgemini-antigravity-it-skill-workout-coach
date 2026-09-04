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

"""Seed Firestore collection with initial IT workout tasks."""

from google.cloud import firestore

# HARDCODED GCP PROJECT ID (Required: Do not use google.auth.default() or GOOGLE_CLOUD_PROJECT)
PROJECT_ID = "qwiklabs-gcp-03-4f265f3b8af7"

SEED_TASKS = [
    {
        "task_id": "task_001",
        "title": "Google Antigravity Skill YAML作成基礎",
        "category": "Antigravity",
        "difficulty": "Beginner",
        "estimated_minutes": 15,
        "description": "Skill.mdのフロントマター（name, description）を定義し、対話型ブレインストーミングSkillを構築する。",
        "status": "completed",
    },
    {
        "task_id": "task_002",
        "title": "Agent CLIによるAgent Runtimeデプロイ演習",
        "category": "Agent CLI",
        "difficulty": "Intermediate",
        "estimated_minutes": 20,
        "description": "agents-cli deployコマンドを実行し、Agent Engine上にエージェントを正常にデプロイする。",
        "status": "in_progress",
    },
    {
        "task_id": "task_003",
        "title": "Agent CLIを活用したM365 Copilotプラットフォーム連携デプロイ",
        "category": "M365 Copilot",
        "difficulty": "Advanced",
        "estimated_minutes": 30,
        "description": "Agent CLIでA2Aプロトコル経由のM365 Copilot連携プラグインを設定し、外部プラットフォームへデプロイする。",
        "status": "not_started",
    },
    {
        "task_id": "task_004",
        "title": "Vertex AI Memory Bankによる長期記憶パラメータ設定",
        "category": "Antigravity",
        "difficulty": "Intermediate",
        "estimated_minutes": 15,
        "description": "PreloadMemoryToolとafter_agent_callbackを実装し、ユーザーの学習設定を全自動記録する。",
        "status": "completed",
    },
]


def seed_firestore():
    """Populates the workout_tasks collection in Firestore with initial seed items."""
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("workout_tasks")

    print(f"Seeding Firestore collection 'workout_tasks' in project '{PROJECT_ID}'...")
    for item in SEED_TASKS:
        doc_ref = collection_ref.document(item["task_id"])
        doc_ref.set(item)
        print(f"  - Seeded task: [{item['task_id']}] {item['title']} ({item['status']})")

    print("Firestore seeding completed successfully!")


if __name__ == "__main__":
    seed_firestore()
