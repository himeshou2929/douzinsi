import csv
import time
from pathlib import Path

import config
from novelai_client import generate_image, NovelAIError

OUTPUT_DIR = Path(__file__).parent / "output"
PROMPTS_CSV = Path(__file__).parent / "prompts.csv"


def main():
    config.require_token()
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(PROMPTS_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"{len(rows)}件のプロンプトを処理します（モデル: {config.MODEL}）")

    for i, row in enumerate(rows, start=1):
        out_path = OUTPUT_DIR / f"{row['id']}.png"
        if out_path.exists():
            print(f"[{i}/{len(rows)}] {row['id']} は既に生成済み、スキップ")
            continue

        print(f"[{i}/{len(rows)}] {row['id']} 生成中...")
        try:
            png_bytes = generate_image(row["prompt"], row.get("negative_prompt", ""))
            out_path.write_bytes(png_bytes)
            print(f"[{i}/{len(rows)}] {row['id']} 完了 -> {out_path}")
        except NovelAIError as e:
            print(f"[{i}/{len(rows)}] {row['id']} 失敗: {e}")

        time.sleep(config.BATCH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
