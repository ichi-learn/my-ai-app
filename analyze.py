import os
from pathlib import Path
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.imageanalysis.models import VisualFeatures

# 環境変数から取得
endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")
image_url = os.getenv("IMAGE_URL")


# ローカルの .env ファイルが存在すれば読み込む（簡易パーサ）
def _load_env_file(path):
    try:
        p = Path(path)
        if p.exists():
            with p.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        v = v.strip().strip('"').strip("'")
                        os.environ.setdefault(k.strip(), v)
    except Exception:
        pass


# プロジェクトルートの .env を読み込む（存在すれば）
_load_env_file(Path(__file__).parent / ".env")

# 必須パラメータの確認
endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")
image_url = os.getenv("IMAGE_URL")

# 必須パラメータの確認
if not endpoint or not key or not image_url:
    print("❌ エラー: AZURE_ENDPOINT、AZURE_KEY、IMAGE_URL を環境変数で設定してください")
    exit(1)

# クライアントの作成
client = ImageAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# 画像の解析
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.CAPTION, VisualFeatures.TAGS]
)

# 結果の表示
print("-" * 30)
if result.caption:
    print(f"AIの説明: {result.caption.text} (確信度: {result.caption.confidence:.2f})")

if result.tags:
    print("検出されたタグ:")
    for tag in result.tags.list:
        print(f" - {tag.name} ({tag.confidence:.2f})")
print("-" * 30)