import io
import zipfile

import requests

import config


class NovelAIError(RuntimeError):
    """NovelAI API呼び出し・レスポンス処理で発生したエラー"""


def generate_image(prompt, negative_prompt="", width=None, height=None, steps=None):
    """NovelAI APIで画像を1枚生成し、PNGのバイト列を返す"""
    config.require_token()

    payload = {
        "input": prompt,
        "model": config.MODEL,
        "action": "generate",
        "parameters": {
            "negative_prompt": negative_prompt,
            "width": width or config.DEFAULT_WIDTH,
            "height": height or config.DEFAULT_HEIGHT,
            "steps": steps or config.DEFAULT_STEPS,
            "n_samples": 1,
            "sampler": config.DEFAULT_SAMPLER,
            "scale": config.DEFAULT_SCALE,
        },
    }
    headers = {
        "Authorization": f"Bearer {config.API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        res = requests.post(
            config.API_URL,
            headers=headers,
            json=payload,
            timeout=config.REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as e:
        raise NovelAIError(f"NovelAIへの接続に失敗しました: {e}") from e

    if not res.ok:
        raise NovelAIError(f"{res.status_code}: {res.text}")

    return _extract_png(res.content)


def _extract_png(zip_bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            names = z.namelist()
            if not names:
                raise NovelAIError("生成結果のZIPが空でした")
            with z.open(names[0]) as f:
                return f.read()
    except zipfile.BadZipFile as e:
        raise NovelAIError(f"生成結果の解凍に失敗しました: {e}") from e
