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

"""Standalone test script for Vertex AI RAG Corpus retrieval."""

import sys
from vertexai.preview import rag
import vertexai

PROJECT_ID = "qwiklabs-gcp-03-4f265f3b8af7"
LOCATION = "us-central1"


def test_retrieval(corpus_name: str, query: str = "Who is the main character?"):
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    print(f"Testing retrieval against {corpus_name} with query: '{query}'...")
    resp = rag.retrieval_query(
        text=query,
        rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
        rag_retrieval_config=rag.RagRetrievalConfig(top_k=3),
    )
    contexts = getattr(resp.contexts, "contexts", [])
    print(f"Found {len(contexts)} passages:")
    for i, c in enumerate(contexts):
        score = getattr(c, "score", 0.0)
        text = getattr(c, "text", "")
        print(f"\n--- Result {i+1} (Score: {score:.4f}) ---")
        print(text[:300] + "...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_rag_retrieval.py <CORPUS_NAME> [QUERY]")
        sys.exit(1)
    corpus = sys.argv[1]
    q = sys.argv[2] if len(sys.argv) > 2 else "What are the key themes described?"
    test_retrieval(corpus, q)
