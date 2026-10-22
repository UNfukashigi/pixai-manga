---
name: pixai-manga
description: PixAI の API（Tsubaki.3）で、1ページの漫画画像（カラー／モノクロ、日本語の縦書きセリフ入り）を生成して保存する。ユーザーの PixAI API キーが必要。「PixAIで漫画を作って」「Tsubaki.3で4コマ」「PixAIのAPIで漫画を生成」などの依頼で使う。LoRA と公式レシピも指定できる（既定はどちらも使わない）。
---

# PixAI 漫画生成スキル

ページ設計図（JSON）から、Tsubaki.3 がよく守る英語の文章プロンプトを組み立て、PixAI の API で漫画1ページを生成して保存する。

## 最初の準備（API キー）

1. PixAI にログインし、API キーを作る（https://pixai.art/profile/edit/api ）
2. キーを環境変数 `PIXAI_API_KEY` に設定する。**キーの文字列をチャットに貼らせない**。ユーザー自身に設定してもらう
   - Windows（PowerShell）：`[Environment]::SetEnvironmentVariable("PIXAI_API_KEY", "<キー>", "User")` を実行し、ターミナルを開き直す
   - macOS / Linux：`~/.zshrc` などに `export PIXAI_API_KEY="<キー>"` を書く
3. 生成には PixAI のクレジットを使う。**初回は、何枚作るかを伝えて確認を取ってから実行する**

## 進め方

1. ユーザーの依頼から、話の内容・登場キャラ・カラー／モノクロ・コマ数を確認する（足りなければまとめて1回で聞く）
2. ページ設計図（JSON）を書く（形式は下。例は `examples/cafe_4koma.json`）
3. `--dry-run` で送るプロンプトを確かめる。WARNING が出たら直す
4. 生成して、画像を見て結果を伝える。うまくいかないところは、下の「うまくいくコツ」で直して作り直す

```bash
python scripts/pixai_manga.py page.json --dry-run
python scripts/pixai_manga.py page.json --out output
python scripts/pixai_manga.py page.json --out output --batch 4   # 4枚作って一番良いものを選ぶ
```

## 既定の設定

- モデル：Tsubaki.3（サイトと同じ版。スクリプトが自動で使う）、品質 `pro`
- 縦横比 2:3・解像度 1.5k。`--xl` でサイトの XL と同じ 1104×1824
- ネガティブプロンプト：`lowres, worst quality, low quality, bad anatomy, explicit`
- **LoRA なし・レシピなし**。プロンプト自動変換（promptHelper）はオフ（オンにするとセリフが崩れ、モノクロに色が混ざった）

## オプション

| オプション | 説明 |
|---|---|
| `--batch 4` | 同じ設定で4枚 |
| `--aspect 3:5` など | 縦横比（1:1, 2:3, 3:2, 3:4, 4:3, 3:5, 5:3, 9:16, 16:9, 1:3, 3:1） |
| `--xl` | 1104×1824（縦横比の指定は使わない） |
| `--mode` | `lite` / `standard` / `pro`（既定）/ `ultra` |
| `--lora <バージョンID>:<重み>` | LoRA（最大5つ、何回でも付けられる）。ユーザーが指定したときだけ使う |
| `--trigger "..."` | LoRA のトリガーワード（プロンプトの最後に足す） |
| `--style <名前>` | 公式レシピ（下の一覧）。ユーザーが指定したときだけ使う |
| `--negative "..."` | ネガティブプロンプト |
| `--seed <数>` | シード |

- **LoRA のバージョンID**：モデルページの URL `pixai.art/model/<モデルID>/<バージョンID>` の後ろ側の番号。モデルIDでは動かない。Tsubaki.3 に対応した版（DiT.3）を使う。URL にモデルIDしかないときは、ページの中の `model/<モデルID>/<バージョンID>` のリンクから拾う
- **公式レシピ**：anime-watercolor-impasto, art-crayon, bold-line-soft-color, chibi, classic-japanese, clean-flat-illustration, colored-pencil-grain, cool-warm-oil-contrast, desaturated-cool, flat-anime-pastel, glossy-glass-anime, grey-blocks-lineless, hard-line-monochrome-accent（白黒に一部だけ色を付ける）, high-contrast-retro-vivid, holographic, korean-style, lineart-watercolor-airy, low-saturation-expressive-eyes, lucid-dreamy, luminous-retro-impasto, minimal-flat-color, modern-oil-glamour, moe-pastel, oil-watercolor-blend, painterly-doodle, paper-watercolor, pencil-sketch, poster-graffiti, retro-comic-fusion, retro-oil-glamour, retro-tv-anime（白黒の漫画に向く）, semi-realistic, stable-vaporwave, tinted-sketch, vintage-collage
- サイトの「レシピマーケット」のレシピは API では使えない（中身が非公開で、API にレシピを指定する項目が無い）

## ページ設計図（JSON）の形式

```json
{
  "color": "color",            // "color" か "mono"
  "mono_finish": "screentone", // mono のときの陰影：screentone / hatching / grayscale / lineart
  "aspect": "2:3",
  "style_prompt": "",          // 絵柄の追加指定（英語）。空なら既定の絵柄
  "characters": [
    {"name": "girl", "label": "the white-haired girl", "look": "1girl, white long hair, ..."}
  ],
  "panels": [
    {
      "layout": "top wide panel",           // コマの位置と大きさ（英語）
      "camera": "Wide Shot, high angle, 35mm lens",
      "scene": "場面の説明（英語）",
      "no_people": false,                    // true で人物を描かないコマ
      "characters": [
        {"name": "girl", "expression": "表情（目と口の形）", "position": "画面上の位置", "pose": "動作と持ち物"}
      ],
      "lighting": "光の向きと影（英語、任意）",
      "effects": ["キラキラ"],               // 集中線・スピード線・キラキラ・汗・どんより など
      "lines": [{"speaker": "girl", "text": "セリフ", "side": "on the right side"}]
    }
  ]
}
```

- `look` は見た目（髪・目・服）。`label` はコマの中での呼び名で、`scene` の中でも同じ呼び名を使う
- 版権キャラは `look` に `sakura miko (hololive)` のように名前と作品名を書くと、かなり再現される（公開・販売の前に、権利者のガイドラインを確認するよう伝える）
- コマ割りの書き方とプロンプトのコツは `references/prompt-guide.md` を読む

## うまくいくコツ（要点。くわしくは references/prompt-guide.md）

- **セリフ以外は英語で書く**。日本語の説明は、絵の中の文字として描かれてしまう
- セリフは短く。崩れたら、言いやすい言葉に言い換えると直ることが多い（例「まだ画面真っ黒だにぇ！？」→「まだ画面うつってないにぇ！？」）。造語や英字の名前は崩れやすい
- 表情は感情の言葉より「目と口の形」で書く。否定も書く（`not smiling`）
- 2人の呼び名は役が分かる言葉にする（名前や A/B だと役が入れ替わった）。片方だけの特徴（片目が隠れる髪など）は、もう片方に `both eyes clearly visible` のように否定で書く
- 破綻しやすいもの（手など）は、描かせない指定にする（`no hands, no arms`）
- モノクロでは色の名前が自動で white / gray / black に置き換わる。光や木の床など色を連想させる描写を減らす。それでも色が残るときは、白黒用の LoRA をユーザーに提案する
- 4枚作って、セリフと絵が一番良いものを選ぶのが現実的

## 注意

- 最終的な絵は AI が決める。指定どおりにならないことがあると伝えておく
- 生成した画像は PixAI 側に長くは残らないので、スクリプトがローカルに保存する
- 実在の人物や既存作品のキャラを使うときは、権利の問題に気をつけるよう伝える
