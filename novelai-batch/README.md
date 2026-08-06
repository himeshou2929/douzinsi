# novelai-batch

NovelAI APIを使った画像生成の検証プロジェクト。Python/Flask + HTML/CSS + NovelAI APIで構成。

## 構成

```
app.py              Flaskアプリ本体（Web UI）
config.py           環境変数・APIデフォルト設定
novelai_client.py   NovelAI API呼び出しロジック
generate.py         CSVからのバッチ生成CLI（prompts.csvを使用）
templates/           base.html / index.html / batch.html
static/css/          style.css（共通スタイル）
static/output/       Web UIでの生成結果（.gitignore対象）
output/               generate.pyでの生成結果（.gitignore対象）
```

## セットアップ

```bash
cd novelai-batch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# .envを開いてNOVELAI_API_TOKENに自分のトークンを設定
```

## 使い方

### Web UI（1枚生成 / まとめて生成）

```bash
python app.py
```

`http://127.0.0.1:5050` にアクセス。

- `/` : プロンプトを1つ入力して1枚生成
- `/batch` : 空行区切りで複数シーン分のプロンプトを入力し、まとめて生成

### CLIバッチ生成

`prompts.csv`（`id,prompt,negative_prompt`列）を用意して実行：

```bash
python generate.py
```

生成済み（`output/`に同名ファイルがある）IDはスキップされる。

## 注意

- `.env`はコミットしないこと（`.gitignore`済み）
- 生成画像（`static/output/`, `output/`）もコミット対象外
