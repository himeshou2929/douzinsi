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

### キャラクター・スタイルを固定したい場合（Vibe Transfer）

どちらの画面でも「キャラ基準画像」「スタイル基準画像」に画像をアップロードすると、NovelAIのVibe Transfer機能でその特徴を反映して生成します。両方同時に指定することも可能です。`/batch`では、アップロードした画像が全シーン共通の基準画像として使われます。

- **キャラ基準画像**: 顔・髪型・服装などキャラクターの見た目を固定したいときに使用
- **スタイル基準画像**: 絵柄・塗り方・線画のタッチを固定したいときに使用
- 参照強度（0〜1）: 大きいほど基準画像に強く寄せる。キャラはデフォルト0.6、スタイルはデフォルト0.3
- 両方指定する場合、2つの強度の合計が1.0以下になるくらいが目安（NovelAI公式の推奨）
- 精度には限界があり、より高精度な固定にはLoRA学習の方が有利（詳細は[docs/](../docs/)の検討メモ参照）

### 生成枚数の指定

`n_samples`（1〜8枚、`config.py`の`MAX_N_SAMPLES`で変更可）で1回のリクエストにつき生成する枚数を指定できます。`/batch`では「シーン数 × 指定枚数」だけ生成されるため、増やすほど時間がかかります。

### CLIバッチ生成

`prompts.csv`（`id,prompt,negative_prompt`列）を用意して実行：

```bash
python generate.py
```

生成済み（`output/`に同名ファイルがある）IDはスキップされる。

## 注意

- `.env`はコミットしないこと（`.gitignore`済み）
- 生成画像（`static/output/`, `output/`）もコミット対象外
