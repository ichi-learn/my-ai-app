# AI借り物競走 🏃‍♂️

GitHub Codespaces で Azure AI Vision を使った画像認識ゲームアプリです。

## 🔒 セキュリティについて

このプロジェクトのコードには、機密情報（API キーやエンドポイント）は含まれていません。すべて環境変数で管理します。

## 📋 セットアップ手順

### 1. 環境変数の設定

`.env.example` をコピーして `.env` ファイルを作成します：

```bash
cp .env.example .env
```

### 2. Azure 情報の設定

`.env` ファイルを編集して、以下の情報を入力します：

```env
AZURE_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com
AZURE_KEY=your-api-key-here
IMAGE_URL=https://your-storage.blob.core.windows.net/images/your-image.png?sp=r&...
```

### 3. 環境変数の読み込み

**Streamlit アプリを実行する場合：**
```bash
# 環境変数を読み込んでから実行
export $(cat .env | xargs)
streamlit run app.py
```

または、OS のシステム設定で環境変数を設定してください。

**analyze.py を実行する場合：**
```bash
export $(cat .env | xargs)
python analyze.py
```

## 📁 ファイル構成

- `app.py` - Streamlit を使ったメインアプリ
- `analyze.py` - 画像解析スクリプト
- `targets.txt` - ゲームのお題リスト
- `.env.example` - 環境変数のテンプレート（このファイルはコミットしてOK）
- `.env` - 実際の環境変数（`.gitignore` で除外）

## ⚠️ 重要

- **`.env` ファイルは絶対に Git にコミットしないでください！**
- `.gitignore` で除外されているため、誤ってコミットされることはありません
- GitHub に上げる際は、`.env.example` のみをテンプレートとして共有してください
