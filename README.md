# douzinsi

同人誌AI量産プロジェクト。企画・検討の背景資料と、実装コードを分けて管理しています。

## 構成

```
docs/            企画メモ・進捗ログ・相談ログ（背景資料、Markdown）
novelai-batch/   NovelAI APIを使った画像生成の実装（Python/Flask）
```

## セットアップ・実行

コードの詳細・セットアップ手順は [novelai-batch/README.md](novelai-batch/README.md) を参照してください。

```bash
cd novelai-batch
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # NOVELAI_API_TOKENを設定
python app.py          # http://127.0.0.1:5050
```

## 注意

- APIトークンなどの秘密情報は `.env` に置き、コミットしないこと（`.gitignore`済み）
- `docs/` には企画段階の相談ログを含みます。センシティブな内容を含むため取り扱いに注意してください
