# Changelog

## [2.0.0] — 2026-03-26

### Changed
- Switched data source from `commands.txt` to `Cyberpunk_2077_Items.xlsx`
- Commands jump from 492 → **6,976** across 13 sections
- Build script rewritten to use `openpyxl` instead of plain-text parsing
- Added new sections: Weapon Mods, Consumables, Vehicles, Teleport Locations, Progression, Misc Commands

### Added
- Vehicles section (85 unlock commands)
- Teleport Locations (423 precise map coordinates)
- Consumables (190 drinks, food, drugs)
- Weapon Mods (279 attachment commands)
- Misc Commands (123 complex Lua scripts — max everything, god mode, etc.)

## [1.0.0] — 2026-03-22

### Initial release
- 492 commands from plain-text file across 14 sections
- Collapsible sections, live search, multi-select, copy output
- Python build script, single offline HTML file
