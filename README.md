# CP2077 Command Builder

Command List Reference: https://www.nexusmods.com/cyberpunk2077/mods/3129?tab=posts

A browser-based tool for building and copying **Cyber Engine Tweaks (CET)** console commands for Cyberpunk 2077. Search, select, and generate multi-item command blocks with one click — no more typing commands manually.

![screenshot](docs/screenshot.png)

---

## Features

- **6,976 commands** across 13 sections — parsed directly from the community Excel spreadsheet
- **Sections collapsed by default** — only expands what you open, nothing overwhelming
- **Live search** — type any keyword and matching items auto-expand across all sections
- **Multi-select** — tick as many items as you want, set your quantity, hit Generate
- **One-click copy** — paste the whole block straight into CET in-game
- **No install, no dependencies** — single HTML file, works offline in any browser

---

## Sections

| Section | Commands |
|---|---|
| Weapons | 1,464 |
| Grenades | 76 |
| Weapon Mods | 279 |
| Cyberware | 1,401 |
| Quickhacks | 79 |
| Clothing | 1,826 |
| Clothing Outfit Sets | 65 |
| Crafting & Recipes | 935 |
| Consumables | 190 |
| Vehicles | 85 |
| Teleport Locations | 423 |
| Progression | 30 |
| Misc Commands | 123 |

---

## Usage

### Option A — Just open the HTML (no build needed)

```
index.html   ← open this in any browser
```

### Option B — Rebuild from the Excel source

Requires Python 3.6+ and openpyxl.

```bash
pip install openpyxl
python src/build.py
```

This parses `data/Cyberpunk_2077_Items.xlsx` and regenerates `index.html`.

---

## Project Structure

```
cp77-command-builder/
├── index.html                       # The ready-to-use tool (open in browser)
├── data/
│   └── Cyberpunk_2077_Items.xlsx    # Source spreadsheet — edit this to add commands
├── src/
│   └── build.py                     # Parser — reads xlsx, generates index.html
├── docs/
│   └── screenshot.png               # Screenshot for README
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## Updating Commands

Drop a new version of `Cyberpunk_2077_Items.xlsx` into the `data/` folder and run:

```bash
python src/build.py
```

That's it. The HTML regenerates automatically with the new data.

---

## Requirements

- **In-game**: [Cyber Engine Tweaks](https://www.nexusmods.com/cyberpunk2077/mods/107) mod installed (PC only)
- **This tool**: Any modern browser — Chrome, Firefox, Edge, Safari
- **Rebuilding**: Python 3.6+ with `openpyxl` (`pip install openpyxl`)

---

## Disclaimer

Console commands require the **Cyber Engine Tweaks** mod and only work on **PC**. Some commands require the **Phantom Liberty DLC**. Always back up your save before using commands. Use at your own risk.

---

## Contributing

1. Fork the repo
2. Update `data/Cyberpunk_2077_Items.xlsx` with new or corrected commands
3. Run `python src/build.py` to verify it builds cleanly
4. Open a PR describing what changed

---

## License

MIT — free to use, modify, and share.
