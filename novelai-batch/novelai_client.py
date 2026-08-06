import os
import zipfile
import io
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_TOKEN = os.getenv("NOVELAI_API_TOKEN", "")
MODEL = os.getenv("NOVELAI_MODEL", "nai-diffusion-4-full")
API_URL = "https://image.novelai.net/ai/generate-image"


def generate_image(prompt, negative_prompt, width=832, height=1216, steps=28):
    if not API_TOKEN:
        raise RuntimeError("NOVELAI_API_TOKENが.envに設定されていません")

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
    if not res.ok:
        raise RuntimeError(f"{res.status_code}: {res.text}")
    return extract_png(res.content)


def extract_png(zip_bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        names = z.namelist()
        if not names:
            raise RuntimeError("生成結果のZIPが空でした")
        with z.open(names[0]) as f:
            return f.read()
