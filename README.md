# pixai-manga

[PixAI](https://pixai.art) の API と画像生成モデル **Tsubaki.3** で、1ページの漫画画像を生成する Claude Code 用のスキルです。

- カラー／モノクロの漫画を、日本語の縦書きセリフ入りで生成
- コマ割り・カメラ・表情・セリフを書いた JSON（ページ設計図）から、Tsubaki.3 がよく守る英語のプロンプトを自動で組み立てる
- LoRA と公式レシピを指定できる（既定はどちらも使わない）
- 生成した画像はローカルに保存

> **非公式のツールです。** PixAI とは関係ありません。PixAI の利用規約と API の規約に従って使ってください。

## 必要なもの

- [Claude Code](https://claude.com/claude-code)
- Python 3.9 以上（標準ライブラリだけで動きます）
- PixAI のアカウントと API キー（生成には PixAI のクレジットを使います）

## インストール

`pixai-manga` フォルダを、Claude Code のスキルのフォルダにコピーします。

- Windows：`%USERPROFILE%\.claude\skills\pixai-manga`
- macOS / Linux：`~/.claude/skills/pixai-manga`

## API キーの設定

1. PixAI にログインし、[API の設定ページ](https://pixai.art/profile/edit/api)でキーを作ります
2. 環境変数 `PIXAI_API_KEY` に設定します

Windows（PowerShell）：

```powershell
[Environment]::SetEnvironmentVariable("PIXAI_API_KEY", "<あなたのキー>", "User")
```

macOS / Linux（`~/.zshrc` や `~/.bashrc` に追記）：

```bash
export PIXAI_API_KEY="<あなたのキー>"
```

設定したら、ターミナルと Claude Code を開き直してください。キーは他人に見せたり、チャットに貼ったりしないでください。

## 使い方

Claude Code に話しかけるだけで使えます。

> PixAIで、カフェでメイドがラテアートを失敗する4コマ漫画を作って

スクリプトを直接使うこともできます。

```bash
python scripts/pixai_manga.py examples/cafe_4koma.json --dry-run   # 送るプロンプトを確認（クレジットを使わない）
python scripts/pixai_manga.py examples/cafe_4koma.json --out output
python scripts/pixai_manga.py examples/cafe_4koma.json --batch 4   # 4枚作って選ぶ
```

主なオプション：

| オプション | 説明 |
|---|---|
| `--batch 4` | 同じ設定で4枚 |
| `--aspect 3:5` | 縦横比（1:1, 2:3, 3:2, 3:4, 4:3, 3:5, 5:3, 9:16, 16:9, 1:3, 3:1） |
| `--xl` | 1104×1824 で生成 |
| `--mode pro` | 品質（lite / standard / pro / ultra。既定 pro） |
| `--lora <バージョンID>:<重み>` | LoRA（Tsubaki.3 / DiT.3 対応のもの。最大5つ） |
| `--trigger "..."` | LoRA のトリガーワード |
| `--style retro-tv-anime` | 公式レシピ |
| `--seed 12345` | シード |

ページ設計図の書き方は [SKILL.md](SKILL.md) と [references/prompt-guide.md](references/prompt-guide.md) を見てください。

## 中身

```
pixai-manga/
├── SKILL.md                    スキルの説明（Claude Code が読む）
├── scripts/pixai_manga.py      生成スクリプト
├── references/prompt-guide.md  Tsubaki.3 の漫画プロンプトの書き方
└── examples/cafe_4koma.json    ページ設計図の例
```

## 注意

- 使うモデルは Tsubaki.3（[モデルページ](https://pixai.art/ja/model/2024383378759147749/2024383379556065549)、バージョンID `2024383379556065549`）です
- 一部の設定（`width` / `height` による 1104×1824 の指定など）は、[公式の API ドキュメント](https://platform.pixai.art/ja/docs)にまだ載っていない動きを使っています。PixAI 側の変更で動かなくなることがあります
- サイトの「レシピマーケット」のレシピは、API では使えません（公式レシピ35種類だけ使えます）
- 生成される絵やセリフは AI が決めるため、指定どおりにならないことがあります
- 実在の人物や既存作品のキャラクターを使うときは、権利者のガイドラインを確認してください

## ライセンス

[MIT License](LICENSE)
