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

"""Create a serverless Vertex AI RAG Corpus and import files from GCS."""

from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr
import vertexai

PROJECT_ID = "qwiklabs-gcp-03-4f265f3b8af7"
LOCATION = "us-central1"
GCS_PATH = "gs://antigravity-it-workout-coach-assets-4f265f3b/rag/"

PARSING_PROMPT = (
    "Extract useful facts and key content described in this text. "
    "Ignore and omit boilerplate, headers, and footers. "
    "Output clean, self-contained text."
)


def main():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # 1. Switch the region's RAG managed DB to serverless mode (project-level, once).
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    print("Updating RAG Engine config to serverless mode...")
    rag.update_rag_engine_config(
        rag_engine_config=rag.RagEngineConfig(
            name=cfg,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        )
    )

    # 2. Create the corpus.
    print("Creating RAG Corpus 'gutenberg-corpus'...")
    corpus = rag.create_corpus(
        display_name="gutenberg-corpus",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    print(f"Corpus created successfully: {corpus.name}")

    # 3. Import + parse + chunk + embed.
    print(f"Importing files from {GCS_PATH}...")
    resp = rag.import_files(
        corpus_name=corpus.name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-2.5-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print(f"Import finished. Response: {resp}")
    print(f"RESULT_CORPUS_NAME={corpus.name}")
    return corpus.name


if __name__ == "__main__":
    main()
