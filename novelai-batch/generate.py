import os
import csv
import time
import zipfile
import io
from pathlib import Path
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_TOKEN = os.getenv("NOVELAI_API_TOKEN", "")
MODEL = os.getenv("NOVELAI_MODEL", "nai-diffusion-4-full")
API_URL = "https://image.novelai.net/ai/generate-image"

OUTPUT_DIR = Path(__file__).parent / "output"
PROMPTS_CSV = Path(__file__).parent / "prompts.csv"


def generate_image(prompt, negative_prompt, width=832, height=1216, steps=28):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "input": prompt,
        "model": MODEL,
        "action": "generate",
        "parameters": {
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "n_samples": 1,
            "sampler": "k_euler_ancestral",
            "scale": 5,
        },
    }
    res = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    res.raise_for_status()
    return res.content


def save_image_from_zip(zip_bytes, out_path):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        names = z.namelist()
        if not names:
            raise RuntimeError("生成結果のZIPが空でした")
        with z.open(names[0]) as f, open(out_path, "wb") as out:
            out.write(f.read())


def main():
    if not API_TOKEN:
        raise RuntimeError("NOVELAI_API_TOKENが.envに設定されていません")

    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(PROMPTS_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"{len(rows)}件のプロンプトを処理します（モデル: {MODEL}）")

    for i, row in enumerate(rows, start=1):
        out_path = OUTPUT_DIR / f"{row['id']}.png"
        if out_path.exists():
            print(f"[{i}/{len(rows)}] {row['id']} は既に生成済み、スキップ")
            continue

        print(f"[{i}/{len(rows)}] {row['id']} 生成中...")
        try:
            zip_bytes = generate_image(row["prompt"], row.get("negative_prompt", ""))
            save_image_from_zip(zip_bytes, out_path)
            print(f"[{i}/{len(rows)}] {row['id']} 完了 -> {out_path}")
        except Exception as e:
            print(f"[{i}/{len(rows)}] {row['id']} 失敗: {e}")

        time.sleep(3)


if __name__ == "__main__":
    main()
