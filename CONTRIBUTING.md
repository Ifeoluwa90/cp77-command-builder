# Contributing

Thanks for helping improve the CP2077 Command Builder!

## Quickest contribution — fixing or adding commands

All commands live in `data/commands.txt`. The format is straightforward:

```
Game.AddToInventory("Items.SomeItem", 1)  | What this item does / what it is
Items.AnotherItem                          | Shorter form — quantity defaults to 1
```

Just edit the file, run `python src/build.py` to confirm it parses cleanly, then open a PR.

## Adding a new section

1. Open `data/commands.txt`
2. Add a new section block following the existing pattern:

```
================================================================
 SECTION N — YOUR NEW SECTION NAME
================================================================

COMMAND                              | WHAT IT DOES
-------------------------------------|----------------------------------------------
Game.AddToInventory("Items.Foo", 1)  | Description
```

3. Run `python src/build.py` and confirm it appears in `index.html`

## Reporting wrong item IDs

Open an issue with:
- The item name
- The incorrect ID currently in the file
- The correct ID (link to source if possible — Cyberpunk wiki, CET wiki, etc.)

## Pull request checklist

- [ ] `python src/build.py` runs without errors
- [ ] New commands tested in-game where possible
- [ ] Descriptions are clear and concise
- [ ] No duplicate item IDs added
