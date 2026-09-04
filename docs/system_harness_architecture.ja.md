# 🏛️ システムプロンプト・ハーネス設計・環境復元アーキテクチャガイド

本ドキュメントは、**IT Skill Workout Coach** エージェントのシステムプロンプト構成、環境設定、実験運用ハーネス設計、VM 初期化手順、復元可能な実データセット、および **デモ動画自動録画・生成パイプラインの実現メカニズム** を体系的に解説した技術仕様書です。

---

## 1. ⚙️ Antigravity Lab 設定・プロンプト一覧

### 1. 認証・環境設定ファイル

- **`lab.env`** (`/config/automata/lab.env`): Qwiklabs受講者アカウント (`AG_EMAIL`, `AG_PASSWORD`) および GCP プロジェクト ID (`AG_PROJECT_ID`)。
- **アプリ用 `.env`** (`/config/Desktop/BuildWithGemini/antigravity-it-skill-workout-coach/.env`): Vertex AI / GCP 設定:
  ```env
  GOOGLE_GENAI_USE_VERTEXAI=true
  GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-03-4f265f3b8af7
  GOOGLE_CLOUD_LOCATION=global
  MEMORY_BANK_ID=7139003105068187648
  ```

### 2. システムプロンプト・要件定義

- **`agent.py (instruction)`**: IT Skill Workout Coach エージェントのペルソナおよび A2UI カードフォーマット出力命令。
- **`project_brief.md`** (`/config/Desktop/BuildWithGemini/project_brief.md`): コア要件（長期記憶、ツール、評価、デプロイ、フロントエンド）および発展機能（A2UI カード、画像生成バッジ、コード実行グラフ）の仕様書。
- **`GEMINI.md`** (`/config/Desktop/BuildWithGemini/antigravity-it-skill-workout-coach/GEMINI.md`): AI エージェント開発ガイドライン（6 フェーズ開発フロー、CLI コマンド、運用制約ルール）。
- **`SKILL.md (troubleshoot-lab-setup)`** (`/config/Desktop/BuildWithGemini/.agents/skills/troubleshoot-lab-setup/SKILL.md`): GCP ログイン状態、IAM 権限 (`roles/aiplatform.user`)、有効 API の事前チェック・自動診断プロンプト。

### 3. 自動化スクリプト・インターセプター・マーカー

- **`automata/bin/`**:
  - `ag_autologin.py`: GCP および Antigravity CLI への自動ログイン制御スクリプト。
  - ブラウザインターセプター (`xdg-open`, `shim`): リモートデスクトップ環境におけるブラウザ起動呼出のインターセプト。
- **`.antigravity-lab-setup-complete`** (`/config/.antigravity-lab-setup-complete`): Lab 環境の初期化完了を示す完了フラグファイル。

---

## 2. 🤖 エージェントのシステムプロンプト構造

[`app/agent.py`](../app/agent.py) で定義されるレイヤードシステムプロンプトの構成です。

### システム指示 (`a2ui_instruction`)

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

## 3. ⚙️ インフラストラクチャ・IAM 権限設定

### プロジェクト設定 (`agents-cli-manifest.yaml`)

```yaml
agent_directory: app
project_id: qwiklabs-gcp-03-4f265f3b8af7
location: us-east1
staging_bucket: gs://qwiklabs-gcp-03-4f265f3b8af7-agent-staging
```

### 付与された IAM 権限

- `roles/datastore.user`: Firestore 読取/書込用。
- `roles/storage.objectAdmin`: パブリック GCS アセットバケット (`antigravity-it-workout-coach-assets-4f265f3b`) アクセス用。
- `roles/aiplatform.user`: Cloud Run から Vertex AI Reasoning Engine を A2A プロトコル経由で呼び出すため。

---

## 4. 🧪 実験運用ハーネス (Lab Operations Harness) 設計・実装

アーキテクチャの全貌：

```
[ブラウザ UI (index.html)]
       │ (HTTP POST /chat)
       ▼
[FastAPI Gateway プロキシ (main.py)]
       │ (A2A プロトコル / StreamQuery)
       ▼
[Agent Platform Runtime (us-east1)] ──► [Firestore / GCS / RAG]
       │
       ▼
[Playwright & 音声合成エンジン] ──► [FFmpeg 映像パイプライン] ──► [GIF / MP4]
```

---

## 5. 🎬 自動録画デモ動画パイプラインの実現メカニズム（詳細仕様）

本エージェントのデモ動画の自動録画・音源合成・GIF変換パイプラインは、以下の要求プロンプトを満たすよう設計されています：

> *"Record a demo video of my agent. Show it doing the thing my app does best, then ask a second, richer prompt that shows off a tool call, a database lookup, or a generated image."*

このパイプラインは、以下の **5 つのシステムフェーズ** により確定的に自動実行・生成されています：

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. Playwright 自動ブラウザ操作 (scratch/record_demo.py)                                 │
│    ├── フェーズ A: record_video_dir 付き Headless Chromium 起動 (1280x720 画面解像度)     │
│    ├── フェーズ B: プロンプト 1 (Firestore 参照): "Antigravityカテゴリのタスク一覧"        │
│    │            └── DOM .a2card 描画待機 (list_workout_tasks ツール実行)               │
│    └── フェーズ C: プロンプト 2 (画像生成): "Antigravityアチーブメントバッジ生成"          │
│                 └── ツール待機 (gemini-3.1-flash-lite-image -> GCS -> <img> 表示)       │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │ (録画 WebM 生データ)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. 完全 Python アルゴリズム音源合成エンジン (scratch/generate_lofi_music.py)           │
│    ├── 和音進行: Cmaj7 - Am7 - Dm7 - G7 (正弦波オシレータ + RC ローパスフィルタ)          │
│    ├── 84 BPM パーカッション (周波数スイープ Kick、ノイズ Burst Snare、Hi-Hat)         │
│    └── アナログレコードノイズ (Poisson ノイズ + Pink ノイズ) -> lofi_music.wav          │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │ (20秒 ステレオ 44.1kHz WAV 音源)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. FFmpeg 映像エンコード & 2 パス Palette GIF 最適化エンジン                              │
│    ├── 映像・音声マルチプレクス: demo_lofi.mp4 (H.264/AAC) & demo_lofi.webm (VP9/Opus)   │
│    └── 2 パス Palette 変換: palettegen/paletteuse @ 15 FPS -> demo.gif                   │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │ (軽量インライン GIF アセット)
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. インライン プレゼンテーション層                                                      │
│    └── README.md 先頭への相対パス埋め込み ![Demo](./demo.gif)                            │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### フェーズ 1: ブラウザ自動化とシナリオオーケストレーション (`scratch/record_demo.py`)
- `playwright.async_api` を使用し、`record_video_dir` を有効化した Chromium ブラウザ（解像度 1280x720）をバックグラウンド起動。
- ローカルの FastAPI チャット UI (`http://127.0.0.1:8080`) へ自動アクセス。

### フェーズ 2: 2 段階のプロンプト実行シーケンス
1. **ステージ 1 (アプリのコア機能・データベース参照表示)**:
   - 送信メッセージ: `"Antigravityカテゴリのワークアウトタスク一覧を表示して"`
   - ツール呼び出し: Firestore データベースからタスクを検索する `list_workout_tasks` を発火。
   - UI 描画: 返された A2UI JSON を解析し、カテゴリ・難易度・進捗ステータス付きのスタイリッシュな `.a2card` コンポーネントを表示。
   - 視認性保持: 動画上で表示を確認できるよう 6 秒間一時停止。
2. **ステージ 2 (リッチなツール呼び出し & マルチモーダル画像生成)**:
   - 送信メッセージ: `"Antigravityマスター達成のアチーブメントバッジ画像を生成して"`
   - ツール呼び出し: Vertex AI 上の `gemini-3.1-flash-lite-image` を呼び出す `generate_workout_badge_image` を発火。
   - アセット保存 & UI 描画: 生成された画像バイナリをパブリック GCS バケット (`antigravity-it-workout-coach-assets-4f265f3b`) へアップロードし、チャット画面上に `<img>` 要素としてインライン表示。
   - 視認性保持: バッジデザインを確認できるよう 8 秒間一時停止。

### フェーズ 3: 完全 Python 実装 84 BPM Lo-Fi 音源合成エンジン (`scratch/generate_lofi_music.py`)
外部の有料音楽生成 API やライセンス制約を回避するため、`numpy` と `scipy.io.wavfile` を用いて 84 BPM の Lo-Fi Hip Hop トラックをコードで直接合成：
- **和音進行**: Cmaj7 - Am7 - Dm7 - G7 のコード進行を、複波形正弦波オシレータと RC ローパスフィルタ処理により温かみのあるチル系サウンドで生成。
- **パーカッション合成**:
  - キック: 周波数スイープ（120 Hz → 40 Hz）による重低音ドラム。
  - スネア: 指数減衰エンベロープを適用したフィルタ処理ホワイトノイズ。
  - ハイハット: 8 分音符サブビートに配置されたハイパスノイズ Burst。
- **ヴィンテージノイズ**: ポアソンインパルスノイズとピンクノイズを重畳し、アナログレコードのレコードノイズ（Vinyl Crackle）を再現。

### フェーズ 4: FFmpeg エンコード & 2 パス Palette GIF 最適化
- **マルチプレクス**: 録画した WebM 映像と合成 WAV 音声を FFmpeg で結合（MP4: `-c:v libx264 -c:a aac` / WebM: `-c:v libvpx-vp9 -c:a libopus`）。
- **2 パス Palette GIF 最適化**:
  - パス 1: 256 色の最適カラーパレットを生成 (`palettegen`)。
  - パス 2: Bayer ディザリングを適用した パレットマッピング (`paletteuse`) を 15 FPS / 幅 800px で実行。
  - 成果: 高画質・滑らかなループ再生が可能な軽量 GIF (`./demo.gif`, < 3 MB) を生成。

### フェーズ 5: インライン プレゼンテーション層
- `README.md` の冒頭に相対パス `![Demo](./demo.gif)` で埋め込み、GitHub や各種 Markdown 閲覧環境で無音かつ滑らかに自動ループ再生される構成を実現。

---

## 6. 📦 復元可能な実データセット (Reproducible Real Datasets)

### 1. Firestore タスク初期シードデータ (`docs/seed_data/firestore_tasks.json`)
エージェントがタスク参照・ステータス更新機能で使用する Firestore データベースの初期データセット。

### 2. エージェント自動評価用データセット (`tests/eval/datasets/workout-coach-dataset.json`)
タスク一覧取得、アチーブメントバッジ生成、動画ティーザー生成、およびスキルガイド回答の正確性を自動検証するためのマルチターン評価テストケース。
