import os
import random
from pathlib import Path
import streamlit as st

from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

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

# 1. ページの設定（ブラウザのタブに表示される名前など）
st.set_page_config(page_title="AI借り物競走", page_icon="🏃‍♂️")

st.title("AI借り物競走 🏃‍♂️")

# 2. Azure AI 設定
# 環境変数から取得（必須：環境変数を設定してください）
ENDPOINT = os.getenv("AZURE_ENDPOINT")
KEY = os.getenv("AZURE_KEY")

if not ENDPOINT or not KEY:
    st.error("❌ エラー: AZURE_ENDPOINT と AZURE_KEY を環境変数で設定してください")
    st.stop()

# AIクライアントの初期化（ENDPOINT/KEY が設定されていれば接続を試みます）
client = ImageAnalysisClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))

# 3. ゲーム画面の表示
# ターゲットリストを外部ファイルで管理（targets.txt）。見つからない場合はデフォルトを使用。
targets_path = Path(__file__).parent / "targets.txt"
try:
    with open(targets_path, "r", encoding="utf-8") as f:
        targets = [line.strip() for line in f.readlines() if line.strip()]
except Exception:
    targets = ["Coffee (コーヒー)"]

if "current_target" not in st.session_state:
    st.session_state.current_target = random.choice(targets)

# ボタン用コールバックでターゲット更新（レンダリング順の不整合を防ぐ）
def _next_target():
    st.session_state.current_target = random.choice(targets)

col1, col2 = st.columns([3,1])
with col1:
    st.header(f"今のお題：『{st.session_state.current_target}』")
with col2:
    st.button("次のお題", on_click=_next_target)

st.write(f"身の回りにある『{st.session_state.current_target}』に関係するものを写真に撮って送ってください！")

# 画像アップロード用のボタンを表示
uploaded_file = st.file_uploader("写真をアップロード、または撮影", type=["jpg", "jpeg", "png"])

# 画像がアップロードされたら実行
if uploaded_file is not None:
    from PIL import Image
    import io

    # アップロードファイルをバイトとして読み取る
    uploaded_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(uploaded_bytes))
    st.image(image, caption="アップロードされた画像", use_column_width=True)

    # エンドポイント/キーが未設定の場合は案内を表示して解析を行わない
    if not ENDPOINT or not KEY:
        st.write("画像を受け取りました。Azureで解析する場合はエンドポイントとキーを設定してください。")
    else:
        try:
            # 画像バイト列を渡す（ImageAnalysisClient の analyze を使用）
            try:
                analysis = client.analyze(image=io.BytesIO(uploaded_bytes), visual_features=[VisualFeatures.TAGS, VisualFeatures.CAPTION])
            except TypeError:
                # 一部のバージョンや呼び出しシグネチャの違いに備え、位置引数でも試す
                analysis = client.analyze(io.BytesIO(uploaded_bytes), visual_features=[VisualFeatures.TAGS, VisualFeatures.CAPTION])

            # --- デバッグ出力: 生のレスポンスを確認 ---
            # デバッグ出力: デフォルトは折りたたみ（サイドバーで切替可）。
            # 環境変数 SHOW_DEBUG=1 で初期展開可能。
            try:
                show_debug_env = os.getenv("SHOW_DEBUG", "0").lower() in ("1", "true", "yes")
            except Exception:
                show_debug_env = False

            # サイドバーのトグルで表示を切替（デフォルトは env に従う）
            try:
                show_debug = st.sidebar.checkbox("Show debug output", value=show_debug_env)
            except Exception:
                show_debug = show_debug_env

            with st.expander("DEBUG: raw analysis object (click to expand)", expanded=show_debug):
                st.write("---- DEBUG: raw analysis object ----")
                try:
                    st.write(analysis)

                    if hasattr(analysis, "as_dict"):
                        try:
                            st.write(analysis.as_dict())
                        except Exception:
                            st.write("as_dict() 呼び出しで例外が発生しました")
                    else:
                        try:
                            attrs = [a for a in dir(analysis) if not a.startswith("__")]
                            st.write(attrs)
                        except Exception:
                            st.write("属性一覧の取得に失敗しました")
                except Exception as e:
                    st.write(f"DEBUG 出力エラー: {e}")

            # --- シンプルなタグ抽出と照合 (新しい ImageAnalysisClient 互換) ---
            tags = []
            caption_text = ""

            # 新しい SDK の場合: result.tags.list, result.caption が使える
            try:
                if getattr(analysis, "tags", None) and getattr(analysis.tags, "list", None):
                    tags = [getattr(t, "name", str(t)).lower() for t in analysis.tags.list if t is not None]
            except Exception:
                tags = []

            try:
                if getattr(analysis, "caption", None):
                    caption_text = getattr(analysis.caption, "text", "").lower()
            except Exception:
                caption_text = ""

            # 互換性のため、古い SDK のフォーマットにも対応
            if not tags:
                try:
                    if getattr(analysis, "tags", None):
                        tags = [getattr(t, "name", str(t)).lower() for t in analysis.tags if t is not None]
                except Exception:
                    tags = []

            if not caption_text:
                try:
                    if getattr(analysis, "captions", None):
                        caption_text = getattr(analysis.captions[0], "text", "").lower()
                except Exception:
                    caption_text = ""

            st.write("検出タグ:", tags)
            st.write("生成キャプション:", caption_text)

            # 照合は単純なキーワード包含チェック（現在のターゲットからキーワードを派生）
            ct = st.session_state.get("current_target", "coffee").lower()
            target_keywords = [ct]
            if "(" in ct and ")" in ct:
                # 例: "coffee (コーヒー)" -> ['coffee', 'コーヒー']
                main, paren = ct.split("(", 1)
                target_keywords = [main.strip(), paren.rstrip(")").strip()]
            if "（" in ct and "）" in ct:
                main, paren = ct.split("（", 1)
                target_keywords = [main.strip(), paren.rstrip("）").strip()]

            matched = any((kw in ",".join(tags)) or (caption_text and kw in caption_text) for kw in target_keywords)

            if matched:
                st.success("お題と一致しました")
            else:
                st.warning("お題と一致しませんでした。別の写真を試してください。")
        except Exception as e:
            st.error(f"解析エラー: {e}")