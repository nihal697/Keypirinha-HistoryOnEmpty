# Keypirinha-HistoryOnEmpty

Show recent Keypirinha history directly in **Run mode** when the search box is
empty — no `Backspace` out of History mode needed.

## Why

Keypirinha's core is closed-source (the
[Keypirinha/Keypirinha](https://github.com/Keypirinha/Keypirinha) repo is only
a README). `Alt+Space` bound to `hotkey_history` forces you into History scope,
where typing only filters history until you press `Backspace`.

This package takes the open-source route: a Python plugin that suggests your
most recent history items on **empty input in normal Run mode**
(`hotkey_run = Alt+Space`), ready to type immediately.

## Status

* ✅ Slice 1: fork + discovery (core closed, `Keypirinha.history` JSON understood)
* ✅ Slice 2: probe — proved the core never calls plugins on **empty** Run input
  (log: plugin loads, zero `on_suggest` calls), so true history-on-empty is
  impossible without core source. Probe retired.
* ▶ Slice 3 (this commit): keyword plugin — `Alt+Space`, `h`, `Tab` shows the
  most-recent launchable history items, `Enter` runs one via shell-execute.
* ⬜ Slice 4: polish (`max_items`, `history_path` override — both already in
  `historyonempty.ini` — plus `ms-settings:`/`shell:` targets if wanted)

## Usage (Slice 3)

1. Keypirinha tray icon → `Reload Configuration`
2. `Alt+Space`, type `h`, press `Tab` → recent launches, most recent first
3. Type to filter (e.g. `h`, `Tab`, `brav` → Brave), `↑`/`↓`, `Enter` to launch
4. Use `Tab`, not `Space`, to enter the keyword — `space_as_tab` stays off so
   multi-word searches like `file explorer` keep working

Covered: apps and files (`.lnk`, `.exe`, URLs). Skipped for now: internal
commands (`restart`), `ms-settings:` pages, `shell:AppsFolder` apps — the
launcher helper validates local existence first, so those targets can't go
through it (see `_launchable`).

## Dev install (portable)

```powershell
# link live package into the portable profile, then Reload Configuration
New-Item -ItemType SymbolicLink `
  -Path "D:\softwares\keypirinha-2.26-x64-portable\Keypirinha\portable\Profile\Packages\HistoryOnEmpty" `
  -Target "D:\softwares\Keypirinha-HistoryOnEmpty\HistoryOnEmpty"
```

Then in Keypirinha: tray icon → `Reload Configuration`, press `F2` for the
Console, `Alt+Space` with an empty box → expect
`PROBE: empty hook works` + `empty input hook FIRED` in the log.

## Test checklist (Slice 2)

* [ ] `Alt+Space` empty → probe item visible, no `Backspace` needed
* [ ] Typing anything → probe item disappears (normal search unaffected)
* [ ] Console (F2) shows `HistoryOnEmpty probe` lines
* [ ] Existing tests/build unaffected (no core changes — plugin only)
