import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_TOKEN = os.getenv("NOVELAI_API_TOKEN", "")
MODEL = os.getenv("NOVELAI_MODEL", "nai-diffusion-4-full")
API_URL = "https://image.novelai.net/ai/generate-image"

DEFAULT_WIDTH = 832
DEFAULT_HEIGHT = 1216
DEFAULT_STEPS = 28
DEFAULT_SCALE = 5
DEFAULT_SAMPLER = "k_euler_ancestral"

# Vibe Transfer（参照画像によるキャラクター・スタイル一貫性）のデフォルト値
# reference_strength: 参照画像をどれだけ強く反映するか（0-1、大きいほど強い）
# information_extracted: 低いほど構図寄り、高いほど質感・線画などスタイル要素まで転写する
#   （NovelAI公式ドキュメントより。低いと高周波成分＝テクスチャ/スタイルから失われる）
DEFAULT_REFERENCE_STRENGTH = 0.6
DEFAULT_REFERENCE_INFORMATION_EXTRACTED = 1.0
DEFAULT_STYLE_REFERENCE_STRENGTH = 0.3

# 1回のリクエストで生成する枚数
DEFAULT_N_SAMPLES = 1
MAX_N_SAMPLES = 8  # NovelAI側の実際の上限はプラン・モデルにより変動するため安全側の目安値

REQUEST_TIMEOUT_SECONDS = 120
BATCH_INTERVAL_SECONDS = 3


def require_token():
    if not API_TOKEN:
        raise RuntimeError(
            "NOVELAI_API_TOKENが.envに設定されていません。"
            ".env.exampleをコピーして.envを作成し、トークンを設定してください。"
        )
