# 同人誌(AI活用)制作 手順まとめ

元メモ: `~/bikiobrain/事業一覧/同人誌/検討メモ_2026-07-17.md`

## 前提
- 個人で成人向けオリジナルキャラのAI漫画を作る（他人への提供・商材化ではない）
- 形式：漫画（コマ割り・ストーリーあり）、CG集ではない
- **一線**：キャラは必ず成人と明確にわかる設定にする（体型・年齢設定・文脈すべて保守的に）。DLsite/FANZAの禁止ワード（中学生 等）とも一致

---

## 全体工程

```
①構想・台本      → LLM（Claude/ChatGPT）
②ネーム作成       → Procreate/クリスタで構図・セリフ手描き、ChatGPTでセリフ自然化
③画像生成         → ComfyUI（ローカルAPI）
④キャラ一貫性維持  → プロンプト使い回し／IP-Adapter／LoRA学習
⑤吹き出し・文字組み → Pythonスクリプト(Pillow)で後付け合成
⑥最終チェック      → 人力（破綻・規約適合の確認、ここだけ残る）
⑦出品            → DLsite / FANZA 手動アップロード
```

## 制作9段階（参考にした最重要記事：白梟氏note）
1. 構想（3.5〜9h）：キャラ設定・シチュエーション・ジャンル決定、起承転結
2. ネーム作成（4〜8h）：構図とセリフ手描き→ChatGPTでセリフ自然化。目標20〜30P
3. AI画像生成（13〜30h、最重要工程）：キャラLoRA作成が必須（男キャラは不要）
4. 仕上げ〜販売（4〜9h）：セリフ配置・フォント選定、DLsite/FANZA登録（価格目安300〜600円）

---

## 実際にやった環境構築（Mac M5 / 16GB RAM）

1. **Homebrewインストール**（ターミナルで手動、sudo入力必要）
2. Python 3.12導入時にmacOS 26(Tahoe)特有の不具合（pyexpatのlibexpatシンボル不一致）発生
   → `brew install expat` ＋ `install_name_tool` で再リンク ＋ `codesign --force --sign -` で再署名して解決
3. `~/Desktop/AI同人誌/ComfyUI` にComfyUI本体を導入、venv作成、PyTorch含む依存関係インストール
4. **WAI-illustrious-SDXL**（v17.0, 6.46GB）をCivitaiからダウンロードし `checkpoints` フォルダに配置
   - https://civitai.com/models/827184/wai-illustrious-sdxl
5. MPS(Apple Silicon GPU)モードで起動確認、API経由(`/prompt`エンドポイント)でテスト生成に成功
6. GUIの内蔵テンプレート「**SDXLシンプル**」（左サイドバー「テンプレート」→検索「SDXL」→一番左）でBaseのみ有効化し、4コマ構成の画像生成に成功

### 技術的な発見
- ポジティブプロンプト内に `=== Panel 1 ===` のような区切り文字を書くと、Illustrious系モデルが複数コマレイアウトを1枚の中である程度再現できる
- 日本語テキスト（吹き出し内セリフ）は文字化けする → 想定通りの制限
  - Qwen-Image/Z-Image系は日本語に強いがNSFW制限が強くLoRAと「戦う」ため不採用
  - **結論：絵はIllustriousで生成、セリフは別工程(Pillow等)で後付け合成する方針**

---

## 実測ベンチマーク（M5、16GB RAM）
- SDXL 832×1216、20ステップ：初回103秒（モデルロード込み）、定常状態で約80秒/枚
- 参考：RTX5070(NVIDIA)は1024×1024で7秒/枚 → **M5はNVIDIA環境の10倍以上遅い**
- メモリはほぼ限界（16GB中15GB使用、空き87MB程度）

---

## 規模判明→方針転換（100ページ級と判明）

- 目標が100ページ規模と判明（選別込みで数千枚単位の生成が必要）
- M5ローカルでは1000枚で約22時間、3000枚で約67時間 → 物理的に非現実的
- **結論：LoRA学習がほぼ必須（Mac単体では不可・クラウドGPU必須）**

### キャラ統一の3段階
1. プロンプトの外見タグ使い回し（すぐ可、ブレは残る）
2. IP-Adapter（ComfyUIにノード追加、ローカル完結、参考画像に似せる）
   - Load Image → CLIP Vision Loader → IPAdapter Model Loader → IPAdapter Apply → KSampler
   - weight 0.7〜1.0、CLIP Vision=`CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`
3. **LoRA学習**（精度最高、クラウドGPU必須）
   - 学習画像20〜50枚(角度/背景/表情バリエーション、512〜1024px)
   - Kohya-ss使用、`dataset/1_識別子`フォルダ構成、WD14 Taggerで自動キャプション付け

### クラウドGPU移行の見積もり（RunPod）
- RTX4090：Community Cloudで$0.34/時間（約50円/時間）、秒単位課金
- LoRA学習(1〜3h)＋バッチ生成(数時間)＝合計10〜20時間 → **1作品あたり約1,000〜2,000円**
- 注意：Pod停止(Stop)だけだとストレージ課金継続 → 使い終わったら「Terminate(削除)」まで行う

---

## 販売先
- DLsite / FANZA同人（年齢確認・決済・DL配信をプラットフォームが担保）
- コミケ・コミティア等の即売会は生成AI作品を禁止する動きあり → **電子販売オンリー路線**
- 価格：主流300〜500円
- 収益試算(DLsite手数料約35%)：月50本売れて手取り約16,000円／月100本で約32,000円
- 推奨運用：FANZA or DLsite(メイン) ＋ BOOTH(Pixiv導線) ＋ Patreon(サブスク) の複数展開

---

## 現在地（2026-07-20時点）
- 環境構築・テスト生成までは完了
- RunPodアカウント作成・クラウドGPU環境構築はまだこれから（一旦区切りをつけて後日再開予定）

## 次回やること
1. RunPodアカウント作成、LoRA学習環境の構築
2. 空の吹き出し枠のみ生成→Pythonスクリプト(Pillow)で日本語テキスト後付け合成の仕組みを作る
3. パネル区切りプロンプト技法の再現性を複数シーンで検証
4. キャラの見た目を1体確定させ、LoRA学習用データセットを準備

---

## 参考リンク

**最重要記事**
- 白梟氏「AIエロ漫画制作ワークフロー【完全版＋実践ノウハウ】」 https://note.com/panzer03/n/nb93f914d8d76
- nobin氏「ComfyUIワークフロー2025→2026変更点」 https://note.com/nobinlog/n/nbe67e810d0fe
- さなぎランド「2026年版・企画〜販売の完全ガイド」 https://sanagiland.com/create/ai-cg-shu-tsukurikata/

**技術系**
- sakasaai氏「Kohya_ss完全ガイド2026」 https://sakasaai.com/kohya_ss-gui-all/
- sakasaai氏「RunPod版Kohya_ss」 https://sakasaai.com/runpod-kohyalora/
- zenn/zain氏「IP-Adapter完全ガイド」 https://zenn.dev/zain/articles/b9cfaa2464e474
- kazumu氏「Illustrious/Animagineプロンプトガイド」 https://note.com/kazumu/n/n6390a899bdce

**モデル**
- WAI-illustrious-SDXL https://civitai.com/models/827184/wai-illustrious-sdxl

**その他**
- ワークフロー配布サイト：CivitAI／ComfyWorkflows／ComfyHub
