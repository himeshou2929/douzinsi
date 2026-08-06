import io
import zipfile

import requests

import config


class NovelAIError(RuntimeError):
    """NovelAI API呼び出し・レスポンス処理で発生したエラー"""


def generate_images(
    prompt,
    negative_prompt="",
    width=None,
    height=None,
    steps=None,
    n_samples=1,
    references=None,
):
    """NovelAI APIで画像を生成し、PNGバイト列のリストを返す（n_samples枚分）

    references: [{"image_b64": str, "strength": float, "information_extracted": float}, ...]
                Vibe Transferで参照する画像のリスト（最大16枚。キャラ用・スタイル用など
                用途の異なる画像を混ぜて指定できる）
    """
    config.require_token()

    parameters = {
        "negative_prompt": negative_prompt,
        "width": width or config.DEFAULT_WIDTH,
        "height": height or config.DEFAULT_HEIGHT,
        "steps": steps or config.DEFAULT_STEPS,
        "n_samples": _clamp_n_samples(n_samples),
        "sampler": config.DEFAULT_SAMPLER,
        "scale": config.DEFAULT_SCALE,
    }

    if references:
        parameters["reference_image_multiple"] = [r["image_b64"] for r in references]
        parameters["reference_strength_multiple"] = [
            r.get("strength", config.DEFAULT_REFERENCE_STRENGTH) for r in references
        ]
        parameters["reference_information_extracted_multiple"] = [
            r.get("information_extracted", config.DEFAULT_REFERENCE_INFORMATION_EXTRACTED)
            for r in references
        ]

    payload = {
        "input": prompt,
        "model": config.MODEL,
        "action": "generate",
        "parameters": parameters,
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

    return _extract_all_png(res.content)


def _clamp_n_samples(n_samples):
    try:
        n = int(n_samples)
    except (TypeError, ValueError):
        n = 1
    return max(1, min(n, config.MAX_N_SAMPLES))


def _extract_all_png(zip_bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            names = sorted(z.namelist())
            if not names:
                raise NovelAIError("生成結果のZIPが空でした")
            return [z.read(name) for name in names]
    except zipfile.BadZipFile as e:
        raise NovelAIError(f"生成結果の解凍に失敗しました: {e}") from e
