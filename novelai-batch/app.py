import re
import time
from pathlib import Path
from flask import Flask, render_template, request

from novelai_client import generate_image

app = Flask(__name__)

OUTPUT_DIR = Path(__file__).parent / "static" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    error = None

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        negative_prompt = request.form.get("negative_prompt", "").strip()

        if not prompt:
            error = "プロンプトを入力してください"
        else:
            try:
                png_bytes = generate_image(prompt, negative_prompt)
                filename = f"gen_{int(time.time())}.png"
                (OUTPUT_DIR / filename).write_bytes(png_bytes)
                image_url = f"/static/output/{filename}"
            except Exception as e:
                error = str(e)

    return render_template("index.html", image_url=image_url, error=error)


@app.route("/batch", methods=["GET", "POST"])
def batch():
    results = []
    error = None
    long_text = ""
    negative_prompt = ""

    if request.method == "POST":
        long_text = request.form.get("long_text", "")
        negative_prompt = request.form.get("negative_prompt", "").strip()

        # 空行（改行を1行以上はさむ）区切りでシーンごとに分割
        chunks = [c.strip() for c in re.split(r"\n\s*\n", long_text) if c.strip()]

        if not chunks:
            error = "プロンプトを入力してください"
        else:
            ts = int(time.time())
            for i, chunk in enumerate(chunks, start=1):
                entry = {"index": i, "prompt": chunk, "image_url": None, "error": None}
                try:
                    png_bytes = generate_image(chunk, negative_prompt)
                    filename = f"batch_{ts}_{i:02d}.png"
                    (OUTPUT_DIR / filename).write_bytes(png_bytes)
                    entry["image_url"] = f"/static/output/{filename}"
                except Exception as e:
                    entry["error"] = str(e)
                results.append(entry)
                time.sleep(3)

    return render_template(
        "batch.html",
        results=results,
        error=error,
        long_text=long_text,
        negative_prompt=negative_prompt,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5050)
