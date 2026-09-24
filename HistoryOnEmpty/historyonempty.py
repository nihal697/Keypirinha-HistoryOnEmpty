# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu


class HistoryOnEmpty(kp.Plugin):
    """Show recent history when the Run box is empty (probe v0)."""

    ITEMCAT_PROBE = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()

    def on_start(self):
        pass

    def on_catalog(self):
        pass

    def on_suggest(self, user_input, items_chain):
        # Top-level Run mode only (no keyword selected)
        if items_chain:
            return

        # Log every top-level call so we can see in the Console (F2)
        # whether empty input reaches us. Keep it as dbg to avoid noise.
        try:
            self.dbg("HistoryOnEmpty probe: input={!r}".format(user_input))
        except Exception:
            pass

        # Slice 2 probe: only react to empty input
        if user_input and user_input.strip():
            return

        try:
            self.warn("HistoryOnEmpty probe: empty input hook FIRED")
        except Exception:
            pass

        item = self.create_item(
            category=self.ITEMCAT_PROBE,
            label="PROBE: empty hook works",
            short_desc="If you see this on empty Alt+Space, Slice 3 can show real history",
            target="probe",
            args_hint=kp.ItemArgsHint.FORBIDDEN,
            hit_hint=kp.ItemHitHint.IGNORE)

        self.set_suggestions([item], kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, action):
        if item and item.target() == "probe":
            kpu.set_clipboard("HistoryOnEmpty probe works")
