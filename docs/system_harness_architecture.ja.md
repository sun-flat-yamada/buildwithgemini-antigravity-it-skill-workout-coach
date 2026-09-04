# 🏛️ システムプロンプト・ハーネス設計・セットアップアーキテクチャガイド

本ドキュメントは、**IT Skill Workout Coach** エージェントアプリケーションにおける Antigravity 動作環境のシステムプロンプト、VM の初期セットアップ情報、環境設定、ラボ操作ハーネス設計、および復元可能な実データセットについての完全な技術解説を提供します。

---

## 1. ⚙️ Antigravity Lab 設定・プロンプト一覧

### 1. 認証・環境設定ファイル

- **`lab.env`** (`/config/automata/lab.env`): Qwiklabs 受講者アカウント情報 (`AG_EMAIL`, `AG_PASSWORD`) および GCP プロジェクト ID (`AG_PROJECT_ID`) を格納。
- **アプリ用 `.env`** (`/config/Desktop/BuildWithGemini/antigravity-it-skill-workout-coach/.env`): Vertex AI および GCP プロジェクト設定:
  ```env
  GOOGLE_GENAI_USE_VERTEXAI=true
  GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-03-4f265f3b8af7
  GOOGLE_CLOUD_LOCATION=global
  MEMORY_BANK_ID=7139003105068187648
  ```

### 2. システムプロンプト・要件定義

- **`agent.py (instruction)`**: IT Skill Workout Coach エージェントのシステムプロンプトおよび A2UI カード構造化出力の指示文。
- **`project_brief.md`** (`/config/Desktop/BuildWithGemini/project_brief.md`): 演習「Antigravity IT Skill Workout Coach」の要件定義書。基本機能 (memory, tools, eval, deploy, frontend) とストレッチメニュー (A2UI カタログ・テーブル, 画像生成バッジ/図解, Code Sandbox グラフ化) を定義。
- **`GEMINI.md`** (`/config/Desktop/BuildWithGemini/antigravity-it-skill-workout-coach/GEMINI.md`): AI エージェント向け開発ガイドライン、6 段階の開発フェーズ、および動作制約ルール (既存コードの保存、モデル非変更ルールなど)。
- **`SKILL.md (troubleshoot-lab-setup)`** (`/config/Desktop/BuildWithGemini/.agents/skills/troubleshoot-lab-setup/SKILL.md`): 環境事前チェック、GCP ログイン状態・IAM 権限 (`roles/aiplatform.user`)・API 有効化状態の診断およびエラー修復用プロンプト。

### 3. 自動化スクリプト・インターセプター・フラグ

- **`automata/bin/`**:
  - `ag_autologin.py`: GCP および Antigravity CLI への自動ログイン処理スクリプト。
  - ブラウザ起動インターセプター (`xdg-open`, `shim`): リモートデスクトップ環境内でのブラウザ起動呼び出しをフック・制御。
- **`.antigravity-lab-setup-complete`** (`/config/.antigravity-lab-setup-complete`): ラボ環境のセットアップ初期化が正常完了したことを示すマーカーファイル。

---

## 2. 🤖 エージェントシステムプロンプト構造

エージェントのペルソナ、実行制約、および UI 出力フォーマットは、[`app/agent.py`](../app/agent.py) 内で定義された多層構造のシステムプロンプトによって制御されています。

### システム指示文 (`a2ui_instruction`)

```text
あなたはユーザーが Google Antigravity、Agent CLI、M365 Copilot を習得するのを支援する IT Skill Workout Coach です。

【重要】A2UI 指示文:
ユーザーの要求に応答する際は、可能な限り、提供されている A2UI ツール/スキーマを使用して応答を A2UI カードとして構造化出力してください。
タスク一覧、スキルガイド、バッジ画像、動画の表示においては、長文プレーンテキストではなく、リッチな A2UI カードを出力してください。

利用可能なツール:
1. list_workout_tasks: Firestore から IT ワークアウトタスクをクエリ取得します。
2. update_workout_task_status: Firestore 内のタスクステータスを更新します。
3. generate_workout_badge_image: gemini-3.1-flash-lite-image を使用して 3D 達成バッジ画像を生成し、GCS へ公開します。
4. generate_workout_teaser_video: global リージョンの gemini-omni-flash-preview を使用してショート 3D モーション動画ティーザーを生成し、GCS へ公開します。
```

---

## 3. ⚙️ インフラ & IAM 権限構成

### プロジェクト設定 (`agents-cli-manifest.yaml`)

```yaml
agent_directory: app
project_id: qwiklabs-gcp-03-4f265f3b8af7
location: us-east1
staging_bucket: gs://qwiklabs-gcp-03-4f265f3b8af7-agent-staging
```

### 付与された IAM ロール

- `roles/datastore.user`: Firestore への読み書きアクセスのため、Agent Engine および Cloud Run サービスアカウントに付与。
- `roles/storage.objectAdmin`: 公開 GCS バケット（`antigravity-it-workout-coach-assets-4f265f3b`）へのアクセス権としてサービスアカウントに付与。
- `roles/aiplatform.user`: A2A プロトコル経由で Vertex AI Reasoning Engine を呼び出すため、Cloud Run サービスアカウントに付与。

---

## 4. 🧪 ラボ操作ハーネス設計 & 実装 (Harness Design & Implementation)

ラボ操作ハーネスは、ブラウザ UI、ローカル開発環境、GCP サーバーレスインフラ、および自動録画パイプラインを以下の 5 つの専門層を通じて接続・運用しています。

```
[ブラウザ UI (index.html)]
       │ (HTTP POST /chat)
       ▼
[FastAPI ゲートウェイプロキシ (main.py)]
       │ (A2A Protocol / StreamQuery)
       ▼
[Agent Platform Runtime (us-east1)] ──► [Firestore / GCS / RAG Engine]
       │
       ▼
[Playwright & 音声合成エンジン] ──► [FFmpeg 動画パイプライン] ──► [GIF / MP4]
```

### 1. CLI & 評価ハーネス (CLI & Evaluation Harness)
- **`google-agents-cli` (`agents-cli`)**: ローカル Playground サーバー、単体/結合テスト実行環境 (`uv run pytest`)、および評価データセット合成・自動採点 (`agents-cli eval`) を一括制御。

### 2. A2A ゲートウェイ & FastAPI プロキシハーネス (`frontend/main.py`)
- ブラウザからの REST 呼び出しを **A2A プロトコル** (`StreamQuery` / `GenerateStreamResponse`) に変換。
- Google ADC (`google.auth.default()`) を利用して認証を自動処理。

### 3. A2UI コンポーネント描画ハーネス (`frontend/static/index.html`)
- ストリーミング返却される A2UI `surfaceUpdate` JSON ブロックをパース。
- フラットなコンポーネントスキーマ (`Card`, `Column`, `Row`, `Text`, `Image`, `Icon`) を直接 DOM ノードへマッピング (`buildNode`, `renderSurface`)。

### 4. データ & アセットストレージハーネス
- **Firestore ハーネス**: コレクション `workout_tasks` 配下で IT スキルタスクドキュメントを管理。
- **GCS アセットハーネス**: 生成されたバイナリバイトストリームを公開 GCS バケット `antigravity-it-workout-coach-assets-4f265f3b` へ直接アップロードし、公開 HTTPS URL を返却。

### 5. 自動動画 & 音声録画ハーネス
- **Headless Playwright (`record_demo.py`)**: `http://localhost:8080` 上でのブラウザユーザー操作を自動化。
- **SciPy/NumPy 音声合成エンジン (`generate_lofi_music.py`)**: 84 BPM の Lo-Fi Hip Hop トラック (Cmaj7 - Am7 - Dm7 - G7) とレコードノイズをプログラム合成。
- **FFmpeg 処理パイプライン**: 映像・音声ストリームのマルチプレクス、WebM から MP4 への変換、およびパレット最適化ループ GIF を自動生成。

---

## 5. 📦 復元可能な実データセット

### 1. Firestore タスク初期データセット (`docs/seed_data/firestore_tasks.json`)
データベース参照時にエージェントが利用する IT ワークアウトタスクの初期状態を格納。

### 2. エージェント評価データセット (`tests/eval/datasets/workout-coach-dataset.json`)
タスク一覧取得、バッジ生成、動画ティーザー作成、およびスキルガイドの検証を行うためのマルチターン評価テストケースを格納。
