# Tsubaki.3 の漫画プロンプトの書き方

スクリプト（`scripts/pixai_manga.py`）が、ページ設計図からこの形のプロンプトを組み立てる。設計図を書くときの参考にする。

## プロンプトの順番（公式の作例と同じ）

1. ページの宣言：`A high-quality full color Japanese manga page, vertical page composition, professional manga layout with 4 panels, thick black panel borders, clean white gutters, highly finished comic illustration.`
2. コマ割り：`Page layout: panel 1 is the top wide panel, panel 2 is the middle panel, ...` と、全コマの位置と大きさを最初にまとめて書く
3. 読む順：`Japanese manga reading order: panels go from top right to bottom left; dialogue is written vertically.`
4. キャラの定義：`<呼び名>: <見た目>.` を全員分。続けて、見た目を全コマでそろえる・服を入れ替えない、の一文
5. コマごと：`<位置と大きさ> (panel N), <カメラ>: <場面>. <呼び名>: <表情>; <位置>; <動作>. Lighting: ... ` のあと、セリフを独立した行で
   ```
   Place a vertical Japanese oval speech bubble on the right side of panel N, spoken by <呼び名>:
   「セリフ」
   ```
6. 最後に全体の絵柄：`Overall style: ...`（モノクロなら `Black and white only. No color, ...` も）

## コマ割りの言葉（layout）

コマの位置と大きさを英語で書く。一番見せたいコマに `largest` を付ける。

| 形 | layout の例 |
|---|---|
| 横長のコマが縦に並ぶ | `top wide panel` / `middle wide panel` / `bottom wide largest panel` |
| 上の段を左右に分ける | `top right panel` / `top left panel`（右から読む） |
| 縦長のコマ | `top right vertical panel`（2段分の高さ） / `bottom right vertical panel` |
| ページの半分を使う大ゴマ | `bottom wide largest panel, half of the page` |
| 小さく重ねるコマ | `small floating inset panel over panel 3` |

例（4コマ）：
- 縦に3段＋下の大ゴマ：`top wide panel` → `middle panel` → `bottom right vertical panel` → `bottom left largest panel`
- 右に縦長、左に2つ、下に大ゴマ：`top right vertical panel` → `top left panel` → `middle left panel` → `bottom wide largest panel`

日本語の縦書きでは、同じ高さに並ぶコマは右から読む。`panels` の並び順をその順にする。

## カメラ（camera）

距離・角度・レンズを組み合わせて書く。

- 距離：`Extreme Close Up` / `Close Up` / `Upper Body` / `Cowboy Shot` / `Full Body` / `Wide Shot`
- 角度：`eye level` / `high angle`（見下ろす） / `low angle`（見上げる） / `side view` / `back view` / `over the shoulder of ...`
- レンズ：`28mm lens`（広角で迫力） / `50mm lens` / `85mm telephoto lens`（背景がぼける）
- 例：`Cowboy Shot, low angle, over the shoulder of the seated girl, 28mm lens`

## 場面とキャラの書き方

- `scene` は画面に見えるものを書く。主役の置き場所（`lower left foreground`、`center right`）、手前・奥（`fills the foreground`、`small in the distance`）も書ける
- 人物を描かないコマは `no_people: true`。セリフは画面外の声として入れられる
- キャラの行は「表情 → 位置 → 動作」。表情は目と口の形で：
  - 笑顔：`eyes closed in happy upward arcs, mouth wide open in a big laugh`
  - 冷めた顔：`flat unimpressed stare, mouth a straight line, not smiling`
  - 驚き：`eyes wide in shock, mouth wide open, sweat drops flying`
- 効果線などは「このコマの中だけ」と限定される（`Effects inside this panel only: ...`）
- 光（lighting）は向きと影の場所を書く：`backlit by the window, bright rim light on her hair` など

## 絵柄の指定

- カラーの既定：`high-detail manga illustration, anime style, clean lineart, cel shading`
- モノクロの既定：`anime-style manga art, not realistic, clean anime character design with large expressive eyes, bold clean outlines, one single confident contour per edge, deep solid blacks on clothing and hair shadows, high contrast black and white`
  - `mono_finish` で陰影を足す：screentone（網点のトーン） / hatching（斜線とベタ黒） / grayscale（なめらかなグレー） / lineart（線だけ）
  - 冒頭に `(monochrome black and white manga page, no color, no sepia:1.3)` が入る。`(…:1.3)` のような重みは Tsubaki.3 で効く
- `style_prompt` で追加・変更できる（英語）

## モノクロの注意

- 見た目の色の名前は、明るさで white / gray / black に自動で置き換わる（例：orange hair → gray hair、yellow eyes → white eyes）
- 日差し・夕日・木の床・飲み物の色など、色を連想させる描写があると、白黒の指定でも色が付くことがある
- タグだけでは背景の看板などに色が残ることがある。完全な白黒にしたいときは、白黒用の LoRA（DiT.3 対応）を使うと安定する

## うまくいかなかったこと（避ける）

- 日本語の説明やページの狙いをプロンプトに入れる → 絵の中に文字として描かれた
- セリフを長い文の中や重みの括弧の中に入れる → 崩れたり消えたりした
- 1つのコマにセリフを詰め込む → 崩れやすい（2つまでが目安）
- プロンプト自動変換をオンにする → セリフが崩れ、関係ない文字が足された
- 吹き出しを空にして描かせる → 「空にする」が守られないことがあった
