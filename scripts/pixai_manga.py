#!/usr/bin/env python3
"""PixAI の API（Tsubaki.3）で、1ページの漫画画像を生成して保存する。

漫画の内容を書いた JSON（ページ設計図）から、Tsubaki.3 がよく守る英語の文章プロンプトを組み立てて送る。
API キーは環境変数 PIXAI_API_KEY から読む。

使い方:
    python pixai_manga.py page.json --out output
    python pixai_manga.py page.json --dry-run                 # 送るプロンプトを表示するだけ（クレジットを使わない）
    python pixai_manga.py page.json --batch 4                 # 同じ設定で4枚
    python pixai_manga.py page.json --lora <バージョンID>:0.7 --trigger "トリガーワード"
    python pixai_manga.py page.json --style retro-tv-anime    # 公式レシピ
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

API = "https://api.pixai.art"
# サイトの Tsubaki.3 と同じ版。mode は pro が既定（サイトと同じ品質で、文字が崩れにくい）
TSUBAKI3 = "2024383379556065549"
MODES = ["lite", "standard", "pro", "ultra"]
ASPECTS = ["1:1", "2:3", "3:2", "3:4", "4:3", "3:5", "5:3", "9:16", "16:9", "1:3", "3:1"]
# 公式レシピ（style.preset の key）
STYLES = ["anime-watercolor-impasto", "art-crayon", "bold-line-soft-color", "chibi", "classic-japanese",
          "clean-flat-illustration", "colored-pencil-grain", "cool-warm-oil-contrast", "desaturated-cool",
          "flat-anime-pastel", "glossy-glass-anime", "grey-blocks-lineless", "hard-line-monochrome-accent",
          "high-contrast-retro-vivid", "holographic", "korean-style", "lineart-watercolor-airy",
          "low-saturation-expressive-eyes", "lucid-dreamy", "luminous-retro-impasto", "minimal-flat-color",
          "modern-oil-glamour", "moe-pastel", "oil-watercolor-blend", "painterly-doodle", "paper-watercolor",
          "pencil-sketch", "poster-graffiti", "retro-comic-fusion", "retro-oil-glamour", "retro-tv-anime",
          "semi-realistic", "stable-vaporwave", "tinted-sketch", "vintage-collage"]
DEFAULT_NEGATIVE = "lowres, worst quality, low quality, bad anatomy, explicit"

# 絵柄（最後の Overall style に入る）
COLOR_STYLE = "high-detail manga illustration, anime style, clean lineart, cel shading"
MONO_STYLE = ("anime-style manga art, not realistic, clean anime character design with large expressive eyes, "
              "bold clean outlines, one single confident contour per edge, "
              "deep solid blacks on clothing and hair shadows, high contrast black and white")
MONO_FINISHES = {
    "screentone": "black ink lines with halftone screentone shading, dot tones for shadows and backgrounds",
    "hatching": "black ink lines with hatching and cross-hatching, solid blacks, almost no midtones",
    "grayscale": "smooth grayscale shading",
    "lineart": "clean line art only, no shading",
}
# モノクロでは色の名前を明るさで white / gray / black に置き換える（色の言葉が残ると一部に色が付く）
MONO_TONES = {
    "white": ["white", "silver", "platinum", "blonde", "blond", "golden", "gold", "yellow", "cream", "beige", "ivory",
              "light pink", "pink", "pastel", "light blue", "sky blue", "light green", "lavender", "light gray", "light grey"],
    "gray": ["orange", "red", "green", "blue", "aqua", "cyan", "teal", "turquoise", "purple", "violet", "magenta",
             "brown", "light brown", "auburn", "ginger", "copper", "amber", "gray", "grey", "khaki", "olive", "emerald"],
    "black": ["black", "dark brown", "navy", "navy blue", "dark blue", "dark green", "dark red", "crimson", "maroon",
              "dark gray", "dark grey", "charcoal", "dark purple", "jet black", "raven"],
}
EFFECTS = {"集中線": "focus speed lines", "スピード線": "speed lines", "キラキラ": "sparkles", "汗": "sweat drops",
           "どんより": "gloomy vertical lines", "怒りマーク": "anger vein mark", "ハート": "floating hearts"}


def to_mono(text):
    pairs = sorted(((n, t) for t, ns in MONO_TONES.items() for n in ns), key=lambda x: -len(x[0]))
    pat = re.compile(r"\b(" + "|".join(re.escape(n) for n, _ in pairs) + r")\b", re.IGNORECASE)
    look = {n.lower(): t for n, t in pairs}
    return pat.sub(lambda m: look[m.group(1).lower()], text)


def cap(t):
    return t[:1].upper() + t[1:]


def build_prompt(page):
    mono = page.get("color", "color") == "mono"
    chars = page.get("characters", [])
    panels = page["panels"]
    conv = to_mono if mono else (lambda t: t)
    names = {c["name"]: conv(c.get("label") or c["name"]) for c in chars}

    out = []
    if mono:  # 光や物の描写が多いと色が付くので、冒頭で重みを付けて言い切る
        out.append("(monochrome black and white manga page, no color, no sepia:1.3).")
    kind = "black and white" if mono else "full color"
    out.append(f"A high-quality {kind} Japanese manga page, vertical page composition, professional manga layout "
               f"with {len(panels)} panels, thick black panel borders, clean white gutters, highly finished comic illustration.")
    # コマ割りは、各コマの位置と大きさを言葉でまとめて書く
    out.append("Page layout: " + ", ".join(f"panel {i} is the {p['layout']}" for i, p in enumerate(panels, 1))
               + ". Japanese manga reading order: panels go from top right to bottom left; dialogue is written vertically.")
    if chars:
        out.append(f"{len(chars)} characters appear. "
                   + " ".join(f"{cap(names[c['name']])}: {conv(c['look']).strip().rstrip(',. ')}." for c in chars)
                   + " Character proportions, faces, hairstyles and outfits stay perfectly consistent across all panels. "
                   "Never swap or mix clothing items between characters.")

    for i, p in enumerate(panels, 1):
        t = f"\n{cap(p['layout'])} (panel {i})"
        if p.get("camera"):
            t += f", {p['camera']}"
        t += ":"
        if p.get("scene"):
            t += f" {conv(p['scene']).rstrip('. ')}."
        if p.get("no_people"):
            t += " No people in this panel: only objects and background."
        for c in p.get("characters", []):
            who = names.get(c["name"], c["name"])
            # 表情を先頭に（目と口の形で書くと守られやすい）
            bits = [x for x in (c.get("expression"), c.get("position"), c.get("pose")) if x]
            if bits:
                t += f" {cap(who)}: {'; '.join(bits)}."
        if p.get("lighting"):
            t += f" Lighting: {p['lighting'].rstrip('.')}."
        if p.get("effects"):
            t += " Effects inside this panel only: " + ", ".join(EFFECTS.get(e, e) for e in p["effects"]) + "."
        # セリフはコマの最後に、独立した行で書く（文の中に入れると崩れたり消えたりした）
        lines = p.get("lines", [])
        for k, l in enumerate(lines, 1):
            who = names.get(l["speaker"], l["speaker"])
            side = ("on the right side (read first)" if k == 1 else "to the left of the previous bubble") if len(lines) > 1 \
                else l.get("side", "near the speaker")
            t += f"\nPlace a vertical Japanese oval speech bubble {side} of panel {i}, spoken by {who}:\n「{l['text']}」"
        out.append(t)

    style = page.get("style_prompt", "")
    if mono:
        style = ", ".join(x for x in (style, MONO_STYLE, MONO_FINISHES.get(page.get("mono_finish", "screentone"), "")) if x)
    else:
        style = style or COLOR_STYLE
    out.append(f"\nOverall style: {style}.")
    if mono:
        out.append("Black and white only. No color, no colored hair or eyes.")
    return " ".join(out).replace(" \n", "\n")


def check(page):
    warns = []
    for i, p in enumerate(page["panels"], 1):
        if not p.get("layout"):
            warns.append(f"コマ{i}: layout（位置と大きさ）がありません")
        texts = [p.get("scene", ""), p.get("camera", "")] + [c.get(k, "") for c in p.get("characters", [])
                                                              for k in ("expression", "position", "pose")]
        if any(any(ord(ch) > 0x2fff for ch in t) for t in texts if t):
            warns.append(f"コマ{i}: セリフ以外に日本語があります。Tsubaki.3 は絵の中の文字として描くことがあるので、英語で書いてください")
    return warns


def api(method, path, key, body=None):
    req = urllib.request.Request(API + path, method=method, headers={"Authorization": f"Bearer {key}"})
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, data, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode('utf-8', 'replace')[:500]}")


def get_key():
    key = os.environ.get("PIXAI_API_KEY")
    if not key and sys.platform.startswith("win"):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                key = winreg.QueryValueEx(k, "PIXAI_API_KEY")[0]
        except OSError:
            pass
    return key


def main():
    ap = argparse.ArgumentParser(description="PixAI（Tsubaki.3）で1ページの漫画を生成する")
    ap.add_argument("page", help="ページ設計図の JSON")
    ap.add_argument("--out", default="output", help="保存先フォルダ")
    ap.add_argument("--batch", type=int, choices=[1, 4], default=1, help="同じ設定で何枚作るか（1 か 4）")
    ap.add_argument("--aspect", help="縦横比（既定: JSON の aspect、なければ 2:3）")
    ap.add_argument("--xl", action="store_true", help="サイトの XL と同じ 1104×1824 で作る（縦横比は 3:5 相当）")
    ap.add_argument("--size", choices=["1k", "1.5k"], default="1.5k", help="解像度（--xl を使わないとき）")
    ap.add_argument("--mode", choices=MODES, default="pro", help="品質（既定 pro）")
    ap.add_argument("--lora", action="append", default=[], metavar="バージョンID[:重み]",
                    help="LoRA（最大5つ）。モデルページの URL の後ろ側の番号。DiT.3 対応のものを使う")
    ap.add_argument("--trigger", default="", help="LoRA のトリガーワード（プロンプトの最後に足す）")
    ap.add_argument("--style", choices=STYLES, help="公式レシピ")
    ap.add_argument("--negative", default=DEFAULT_NEGATIVE, help="ネガティブプロンプト")
    ap.add_argument("--seed", type=int, help="シード")
    ap.add_argument("--dry-run", action="store_true", help="送るプロンプトを表示するだけ")
    args = ap.parse_args()
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    page = json.loads(Path(args.page).read_text(encoding="utf-8"))
    for w in check(page):
        print(f"WARNING: {w}", file=sys.stderr)
    prompt = build_prompt(page)
    if args.trigger:
        prompt += f" {args.trigger.strip().rstrip(',')}."
    if args.dry_run:
        print(prompt)
        return

    key = get_key()
    if not key:
        print("ERROR: PIXAI_API_KEY が設定されていません（SKILL.md の「最初の準備」を参照）", file=sys.stderr)
        sys.exit(2)
    # プロンプト自動変換（promptHelper）はオフ。オンだとセリフが崩れ、モノクロに色が混ざった
    req = {"modelVersionId": TSUBAKI3, "prompt": prompt, "mode": args.mode, "promptHelper": "disable",
           "negativePrompt": args.negative}
    if args.xl:
        req["width"], req["height"] = 1104, 1824  # aspectRatio とは一緒に送れない
    else:
        aspect = args.aspect or page.get("aspect", "2:3")
        if aspect not in ASPECTS:
            print(f"WARNING: 縦横比 {aspect} は使えないので 2:3 にします", file=sys.stderr)
            aspect = "2:3"
        req["aspectRatio"], req["size"] = aspect, args.size
    if args.batch > 1:
        req["batchSize"] = args.batch
    if args.seed is not None:
        req["seed"] = args.seed
    if args.style:
        req["style"] = {"type": "preset", "key": args.style}
    if args.lora:
        req["loras"] = [{"modelId": v.split(":")[0], "weight": float(v.split(":")[1]) if ":" in v else 1.0}
                        for v in args.lora[:5]]

    try:
        task = api("POST", "/v2/image/create", key, req)
        print(f"受付: task={task['id']}", file=sys.stderr)
        while True:
            time.sleep(3)  # 状態の確認は 1.5 秒に1回以下
            st = api("GET", f"/v1/task/{task['id']}", key)
            if st["status"] in ("completed", "failed", "cancelled"):
                break
        if st["status"] != "completed":
            raise RuntimeError(f"生成に失敗しました: {st['status']}")
    except (RuntimeError, KeyError) as e:
        print(f"ERROR: PixAI がエラーを返しました: {e}", file=sys.stderr)
        sys.exit(3)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    (out / f"{stamp}_prompt.txt").write_text(prompt, encoding="utf-8")
    saved = []
    for i, url in enumerate(st["outputs"]["mediaUrls"], 1):  # PixAI 側の画像はずっとは残らないので保存する
        path = out / f"{stamp}_{i}.png"
        with urllib.request.urlopen(url, timeout=120) as r:
            path.write_bytes(r.read())
        saved.append(str(path))
    print(json.dumps({"saved": saved}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
