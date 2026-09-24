# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import json
import os


class HistoryOnEmpty(kp.Plugin):
    """Recent Keypirinha history as a keyword.

    Flow: Alt+Space, type "h", Tab -> most-recent launches, Enter runs one.
    """

    ITEMCAT_HISTORY = kp.ItemCategory.USER_BASE + 1
    KEYWORD = "history"

    DEFAULT_MAX_ITEMS = 8

    def __init__(self):
        super().__init__()
        self._max_items = self.DEFAULT_MAX_ITEMS
        self._history_path_override = None
        self._entries_cache = None
        self._entries_mtime = None

    def on_start(self):
        self._read_config()

    def on_catalog(self):
        self.on_start()
        self.set_catalog([self.create_item(
            category=kp.ItemCategory.KEYWORD,
            label="History",
            short_desc="Show recently launched items",
            target=self.KEYWORD,
            args_hint=kp.ItemArgsHint.REQUIRED,
            hit_hint=kp.ItemHitHint.IGNORE)])

    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return
        last = items_chain[-1]
        if last.category() != kp.ItemCategory.KEYWORD:
            return
        if (last.target() or "").casefold() != self.KEYWORD:
            return

        needle = (user_input or "").casefold().strip()
        suggestions = []
        for entry in self._recent_entries():
            if needle and needle not in entry["label"].casefold():
                continue
            suggestions.append(self.create_item(
                category=self.ITEMCAT_HISTORY,
                label=entry["label"],
                short_desc=entry["desc"],
                target=entry["target"],
                args_hint=kp.ItemArgsHint.ACCEPTED,
                hit_hint=kp.ItemHitHint.IGNORE))
            if len(suggestions) >= self._max_items:
                break

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, action):
        if not item or item.category() != self.ITEMCAT_HISTORY:
            return
        try:
            kpu.shell_execute(item.target())
        except Exception as exc:
            self.warn("HistoryOnEmpty: failed to launch {!r}: {}".format(
                item.target(), exc))

    # -- config ---------------------------------------------------------
    def _read_config(self):
        try:
            settings = self.load_settings()
        except Exception:
            return
        try:
            self._max_items = settings.get_int(
                "max_items", "main", self.DEFAULT_MAX_ITEMS)
        except Exception:
            self._max_items = self.DEFAULT_MAX_ITEMS
        if self._max_items < 1 or self._max_items > 100:
            self._max_items = self.DEFAULT_MAX_ITEMS
        try:
            custom = settings.get_stripped(
                "history_path", "main", fallback="")
        except Exception:
            custom = ""
        self._history_path_override = custom or None
        self._entries_cache = None
        self._entries_mtime = None

    # -- history --------------------------------------------------------
    def _history_file(self):
        if self._history_path_override:
            if os.path.isfile(self._history_path_override):
                return self._history_path_override
            return None

        candidates = []

        # Live dev layout: <Profile>/Packages/HistoryOnEmpty/*.py,
        # so two levels up from this file's directory is <Profile>.
        try:
            base = os.path.abspath(os.path.dirname(__file__))
            for _ in range(2):
                base = os.path.dirname(base)
            candidates.append(
                os.path.join(base, "User", "Keypirinha.history"))
        except Exception:
            pass

        # Installed mode defaults
        for env_var in ("APPDATA", "LOCALAPPDATA"):
            root = os.environ.get(env_var, "")
            if root:
                candidates.append(os.path.join(
                    root, "Keypirinha", "User", "Keypirinha.history"))

        for path in candidates:
            if path and os.path.isfile(path):
                return path
        return None

    def _recent_entries(self):
        path = self._history_file()
        if not path:
            return []
        try:
            mtime = os.path.getmtime(path)
        except Exception:
            return []
        if self._entries_cache is not None and self._entries_mtime == mtime:
            return self._entries_cache

        entries = []
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            self.warn("HistoryOnEmpty: cannot read history: {}".format(exc))
            return []

        sets = (data.get("sets") or {}).get("items") or []
        by_id = {str(it.get("id")): it for it in sets if "id" in it}

        seen = set()
        for record in reversed(data.get("history") or []):
            item_id = str(record.get("item", ""))
            if not item_id or item_id in seen:
                continue
            seen.add(item_id)
            info = by_id.get(item_id)
            if not info:
                continue
            target = info.get("target", "")
            if not self._launchable(target):
                continue
            label = info.get("label") or record.get("label") or target
            stamp = (record.get("time") or "")[:16].replace("T", " ")
            plugin = info.get("plugin", "")
            desc = "{}  ·  {}".format(stamp, plugin).strip("  ·")
            entries.append({
                "label": label,
                "desc": desc or target,
                "target": target,
            })

        self._entries_cache = entries
        self._entries_mtime = mtime
        return entries

    @staticmethod
    def _launchable(target):
        if not target or not isinstance(target, str):
            return False
        low = target.casefold()
        if low.startswith(("http://", "https://", "ftp://")):
            return True
        # Shell/URI targets (ms-settings:, shell:...) are skipped: the
        # helper used to launch validates local existence first (Slice 3).
        if ":" in target and not os.path.isabs(target):
            if not low.startswith("\\\\"):
                # drive-letter paths like C:\... contain ":" too; keep them
                if len(target) < 2 or target[1] != ":":
                    return False
        try:
            return os.path.exists(target)
        except Exception:
            return False
