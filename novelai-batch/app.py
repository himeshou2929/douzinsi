import base64
import re
import time
from pathlib import Path

from flask import Flask, render_template, request

import config
from novelai_client import generate_images, NovelAIError

app = Flask(__name__)

OUTPUT_DIR = Path(__file__).parent / "static" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _read_image_b64(field_name):
    file = request.files.get(field_name)
    if file and file.filename:
        return base64.b64encode(file.read()).decode("utf-8")
    return None


def _read_float(field_name, default):
    raw = request.form.get(field_name, "").strip()
    if not raw:
        return default
    try:
        return max(0.0, min(1.0, float(raw)))
    except ValueError:
        return default


def _read_n_samples():
    raw = request.form.get("n_samples", "").strip()
    if not raw:
        return config.DEFAULT_N_SAMPLES
    try:
        return max(1, min(int(raw), config.MAX_N_SAMPLES))
    except ValueError:
        return config.DEFAULT_N_SAMPLES


def _read_references():
    """アップロードされたキャラ用・スタイル用の参照画像をreferencesリストにまとめる"""
    references = []

    character_b64 = _read_image_b64("reference_image")
    if character_b64:
        references.append({
            "image_b64": character_b64,
            "strength": _read_float("reference_strength", config.DEFAULT_REFERENCE_STRENGTH),
            "information_extracted": config.DEFAULT_REFERENCE_INFORMATION_EXTRACTED,
        })

    style_b64 = _read_image_b64("style_reference_image")
    if style_b64:
        references.append({
            "image_b64": style_b64,
            "strength": _read_float("style_reference_strength", config.DEFAULT_STYLE_REFERENCE_STRENGTH),
            "information_extracted": config.DEFAULT_REFERENCE_INFORMATION_EXTRACTED,
        })

    return references


def _save_images(png_list, filename_prefix):
    urls = []
    for i, png_bytes in enumerate(png_list, start=1):
        filename = f"{filename_prefix}_{i:02d}.png" if len(png_list) > 1 else f"{filename_prefix}.png"
        (OUTPUT_DIR / filename).write_bytes(png_bytes)
        urls.append(f"/static/output/{filename}")
    return urls


@app.route("/", methods=["GET", "POST"])
def index():
    image_urls = []
    error = None
    prompt = ""
    negative_prompt = ""
    reference_strength = config.DEFAULT_REFERENCE_STRENGTH
    style_reference_strength = config.DEFAULT_STYLE_REFERENCE_STRENGTH
    n_samples = config.DEFAULT_N_SAMPLES

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        negative_prompt = request.form.get("negative_prompt", "").strip()
        references = _read_references()
        reference_strength = _read_float("reference_strength", config.DEFAULT_REFERENCE_STRENGTH)
        style_reference_strength = _read_float("style_reference_strength", config.DEFAULT_STYLE_REFERENCE_STRENGTH)
        n_samples = _read_n_samples()

        if not prompt:
            error = "プロンプトを入力してください"
        else:
            try:
                png_list = generate_images(
                    prompt,
                    negative_prompt,
                    n_samples=n_samples,
                    references=references,
                )
                image_urls = _save_images(png_list, f"gen_{int(time.time())}")
            except NovelAIError as e:
                error = str(e)

    return render_template(
        "index.html",
        image_urls=image_urls,
        error=error,
        prompt=prompt,
        negative_prompt=negative_prompt,
        reference_strength=reference_strength,
        style_reference_strength=style_reference_strength,
        n_samples=n_samples,
        max_n_samples=config.MAX_N_SAMPLES,
    )


@app.route("/batch", methods=["GET", "POST"])
def batch():
    results = []
    error = None
    long_text = ""
    negative_prompt = ""
    reference_strength = config.DEFAULT_REFERENCE_STRENGTH
    style_reference_strength = config.DEFAULT_STYLE_REFERENCE_STRENGTH
    n_samples = config.DEFAULT_N_SAMPLES

    if request.method == "POST":
        long_text = request.form.get("long_text", "")
        negative_prompt = request.form.get("negative_prompt", "").strip()
        references = _read_references()
        reference_strength = _read_float("reference_strength", config.DEFAULT_REFERENCE_STRENGTH)
        style_reference_strength = _read_float("style_reference_strength", config.DEFAULT_STYLE_REFERENCE_STRENGTH)
        n_samples = _read_n_samples()

        # 空行（改行を1行以上はさむ）区切りでシーンごとに分割
        chunks = [c.strip() for c in re.split(r"\n\s*\n", long_text) if c.strip()]

        if not chunks:
            error = "プロンプトを入力してください"
        else:
            ts = int(time.time())
            for i, chunk in enumerate(chunks, start=1):
                entry = {"index": i, "prompt": chunk, "image_urls": [], "error": None}
                try:
                    png_list = generate_images(
                        chunk,
                        negative_prompt,
                        n_samples=n_samples,
                        references=references,
                    )
                    entry["image_urls"] = _save_images(png_list, f"batch_{ts}_{i:02d}")
                except NovelAIError as e:
                    entry["error"] = str(e)
                results.append(entry)
                time.sleep(3)

    return render_template(
        "batch.html",
        results=results,
        error=error,
        long_text=long_text,
        negative_prompt=negative_prompt,
        reference_strength=reference_strength,
        style_reference_strength=style_reference_strength,
        n_samples=n_samples,
        max_n_samples=config.MAX_N_SAMPLES,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5050)
