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

REQUEST_TIMEOUT_SECONDS = 120
BATCH_INTERVAL_SECONDS = 3


def require_token():
    if not API_TOKEN:
        raise RuntimeError(
            "NOVELAI_API_TOKENが.envに設定されていません。"
            ".env.exampleをコピーして.envを作成し、トークンを設定してください。"
        )
