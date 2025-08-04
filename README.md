# prj-p-pdr - 医療パンフレット作成支援デモシステム

医療関連資料（講演会音声、企画書、論文等）から、パンフレット素案の構成を自動生成するデモシステムです。

## 機能

- **ドキュメント処理**: Azure Document Intelligence を使用して PDF、Word、PowerPoint ファイルを解析
- **音声処理**: Deepgram を使用して音声ファイル（MP3等）を文字起こし
- **構成生成**: Gemini API を使用して、入力データから医療パンフレットの構成を自動生成

## セットアップ

### 1. 環境構築

```bash
# Python 仮想環境を有効化
source venv/bin/activate

# 必要なライブラリをインストール
pip install -r requirements_minimal.txt
```

### 2. 環境変数の設定

`.env` ファイルに以下の API キーを設定してください：

```
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_azure_key
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_azure_endpoint
DEEPGRAM_API_KEY=your_deepgram_key
GEMINI_API_KEY=your_gemini_key
```

## 使用方法

### 基本的な使用方法

```bash
python main.py
```

### オプション

```bash
# 入力ディレクトリを指定
python main.py --input-dir path/to/input

# 出力ディレクトリを指定
python main.py --output-dir path/to/output

# 音声処理をスキップ（ドキュメントのみ処理）
python main.py --skip-audio

# ドキュメント処理をスキップ（音声のみ処理）
python main.py --skip-documents
```

## ディレクトリ構造

```
prj-p-pdr/
├── input/                  # 入力ファイル
│   ├── 企画：*.docx       # 企画書
│   ├── 材料：*.pptx       # プレゼン資料
│   ├── 材料：*.mp3        # 音声ファイル
│   └── output_reference/   # 参考構成
│       └── output1.txt     # 構成フォーマット
├── output/                 # 出力ファイル
│   ├── generated_structure.txt  # 生成された構成
│   └── processing_summary.txt   # 処理サマリー
├── src/                    # ソースコード
│   ├── processors/         # 処理モジュール
│   ├── generators/         # 生成モジュール
│   └── utils/             # ユーティリティ
└── logs/                   # ログファイル
```

## 出力形式

生成される構成は以下の形式で出力されます：

- **大構成**: セクション名、文字数目安、概要説明
- **詳細構成**: 書くべき内容の要点、使用する図表、参考文献

## トラブルシューティング

- API キーが正しく設定されているか確認してください
- 入力ファイルが正しい形式（.docx, .pptx, .pdf, .mp3）であることを確認してください
- ログファイル（logs/demo_system.log）でエラーの詳細を確認できます