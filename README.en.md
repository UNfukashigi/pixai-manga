# pixai-manga

[日本語](README.md) | English

A [Claude Code](https://claude.com/claude-code) skill that generates one-page manga images with the [PixAI](https://pixai.art) API and the **Tsubaki.3** image model.

- Generates color or black-and-white manga pages with vertical Japanese dialogue
- Builds an English prompt that Tsubaki.3 follows well from a JSON "page plan" (panel layout, camera, expressions, dialogue)
- Supports LoRAs and official PixAI recipes (neither is used by default)
- Saves the generated images locally

> **This is an unofficial tool** and is not affiliated with PixAI. Please follow PixAI's terms of service and API terms.

## Requirements

- [Claude Code](https://claude.com/claude-code)
- Python 3.9+ (standard library only)
- A PixAI account and API key (generation uses your PixAI credits)

## Installation

Copy the `pixai-manga` folder into your Claude Code skills folder:

- Windows: `%USERPROFILE%\.claude\skills\pixai-manga`
- macOS / Linux: `~/.claude/skills/pixai-manga`

## Setting up your API key

1. Log in to PixAI and create a key on the [API settings page](https://pixai.art/profile/edit/api)
2. Set it as the environment variable `PIXAI_API_KEY`

Windows (PowerShell):

```powershell
[Environment]::SetEnvironmentVariable("PIXAI_API_KEY", "<your key>", "User")
```

macOS / Linux (add to `~/.zshrc` or `~/.bashrc`):

```bash
export PIXAI_API_KEY="<your key>"
```

Restart your terminal and Claude Code afterwards. Never share your key or paste it into a chat.

## Usage

Just ask Claude Code:

> Make a 4-panel manga with PixAI where a maid fails at latte art in a cafe

You can also run the script directly:

```bash
python scripts/pixai_manga.py examples/cafe_4koma.json --dry-run   # show the prompt only (no credits used)
python scripts/pixai_manga.py examples/cafe_4koma.json --out output
python scripts/pixai_manga.py examples/cafe_4koma.json --batch 4   # make 4 and pick the best
```

Main options:

| Option | Description |
|---|---|
| `--batch 4` | Generate 4 images with the same settings |
| `--aspect 3:5` | Aspect ratio (1:1, 2:3, 3:2, 3:4, 4:3, 3:5, 5:3, 9:16, 16:9, 1:3, 3:1) |
| `--xl` | Generate at 1104×1824 |
| `--mode pro` | Quality (lite / standard / pro / ultra; default pro) |
| `--lora <versionId>:<weight>` | LoRA (must support Tsubaki.3 / DiT.3; up to 5) |
| `--trigger "..."` | LoRA trigger words |
| `--style retro-tv-anime` | Official recipe |
| `--seed 12345` | Seed |

See [SKILL.md](SKILL.md) and [references/prompt-guide.md](references/prompt-guide.md) for how to write a page plan (these are written in Japanese).

## Contents

```
pixai-manga/
├── SKILL.md                    Skill description (read by Claude Code)
├── scripts/pixai_manga.py      Generation script
├── references/prompt-guide.md  How to write Tsubaki.3 manga prompts
└── examples/cafe_4koma.json    Example page plan
```

## Notes

- The model is Tsubaki.3 ([model page](https://pixai.art/ja/model/2024383378759147749/2024383379556065549), version ID `2024383379556065549`)
- Some settings (such as 1104×1824 via `width` / `height`) rely on behavior that is not yet in the [official API docs](https://platform.pixai.art/ja/docs). They may stop working if PixAI changes the API
- Recipes from PixAI's Recipe Market cannot be used through the API (only the 35 official recipes can)
- The AI decides the final art and lettering, so results may not match your instructions exactly
- When using real people or characters from existing works, check the rights holder's guidelines

## License

[MIT License](LICENSE)
