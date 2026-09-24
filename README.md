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
* ▶ Slice 2 (this commit): probe — single dummy item proves the empty-query
  `on_suggest` hook fires in Run mode
* ⬜ Slice 3: real history items from `Keypirinha.history` (dedup, file/app
  targets via shell-execute)
* ⬜ Slice 4: polish (`max_items`, ignore-list, non-file targets)

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
