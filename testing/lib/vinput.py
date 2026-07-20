"""Virtual input via /dev/uinput: kernel-level keyboard + mouse.

Works natively under Wayland (events enter through libinput like real
hardware). Requires membership in the `input` group.

The active keyboard layout on this host is German (de); evdev keycodes are
positional US names, so typing maps characters through DE_CHARMAP.
"""

import time

from evdev import UInput, ecodes as e

# --- German layout: char -> (evdev keycode, needs_shift) -------------------
_row = {
    "1": e.KEY_1,
    "2": e.KEY_2,
    "3": e.KEY_3,
    "4": e.KEY_4,
    "5": e.KEY_5,
    "6": e.KEY_6,
    "7": e.KEY_7,
    "8": e.KEY_8,
    "9": e.KEY_9,
    "0": e.KEY_0,
}
_shift_row = {
    "!": e.KEY_1,
    '"': e.KEY_2,
    "$": e.KEY_4,
    "%": e.KEY_5,
    "&": e.KEY_6,
    "/": e.KEY_7,
    "(": e.KEY_8,
    ")": e.KEY_9,
    "=": e.KEY_0,
}
DE_CHARMAP = {}
for ch in "abcdefghijklmnopqrstuvwx":
    DE_CHARMAP[ch] = (getattr(e, f"KEY_{ch.upper()}"), False)
    DE_CHARMAP[ch.upper()] = (getattr(e, f"KEY_{ch.upper()}"), True)
# de layout swaps y/z relative to the US-positional keycode names
DE_CHARMAP.update(
    {
        "y": (e.KEY_Z, False),
        "Y": (e.KEY_Z, True),
        "z": (e.KEY_Y, False),
        "Z": (e.KEY_Y, True),
        " ": (e.KEY_SPACE, False),
        "\n": (e.KEY_ENTER, False),
        "\t": (e.KEY_TAB, False),
        ",": (e.KEY_COMMA, False),
        ";": (e.KEY_COMMA, True),
        ".": (e.KEY_DOT, False),
        ":": (e.KEY_DOT, True),
        "-": (e.KEY_SLASH, False),
        "_": (e.KEY_SLASH, True),
        "+": (e.KEY_RIGHTBRACE, False),
        "*": (e.KEY_RIGHTBRACE, True),
        "#": (e.KEY_BACKSLASH, False),
        "'": (e.KEY_BACKSLASH, True),
        "<": (e.KEY_102ND, False),
        ">": (e.KEY_102ND, True),
    }
)
DE_CHARMAP.update({c: (k, False) for c, k in _row.items()})
DE_CHARMAP.update({c: (k, True) for c, k in _shift_row.items()})

# Friendly key aliases for scenario scripts.
KEYS = {
    "esc": e.KEY_ESC,
    "enter": e.KEY_ENTER,
    "space": e.KEY_SPACE,
    "tab": e.KEY_TAB,
    "lshift": e.KEY_LEFTSHIFT,
    "lctrl": e.KEY_LEFTCTRL,
    "up": e.KEY_UP,
    "down": e.KEY_DOWN,
    "left": e.KEY_LEFT,
    "right": e.KEY_RIGHT,
    "backspace": e.KEY_BACKSPACE,
    "f1": e.KEY_F1,
    "f2": e.KEY_F2,
    "f3": e.KEY_F3,
    "f5": e.KEY_F5,
    "f11": e.KEY_F11,
    "w": e.KEY_W,
    "a": e.KEY_A,
    "s": e.KEY_S,
    "d": e.KEY_D,
    "t": e.KEY_T,
    "e": e.KEY_E,
    "q": e.KEY_Q,
    "m": e.KEY_M,
    "j": e.KEY_J,
    "escape": e.KEY_ESC,
}


class VirtualInput:
    """One virtual keyboard + one virtual mouse, kept open for a session."""

    def __init__(self):
        keycodes = sorted(
            {kc for kc, _ in DE_CHARMAP.values()}
            | set(KEYS.values())
            | {getattr(e, f"KEY_F{i}") for i in range(1, 13)}
        )
        self.kbd = UInput({e.EV_KEY: keycodes}, name="cometcroft-e2e-kbd")
        self.mouse = UInput(
            {
                e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE],
                e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL],
            },
            name="cometcroft-e2e-mouse",
        )
        time.sleep(0.8)  # let libinput pick the devices up

    def close(self):
        self.kbd.close()
        self.mouse.close()

    # --- keyboard ---------------------------------------------------------
    def _emit_key(self, dev, code, value):
        dev.write(e.EV_KEY, code, value)
        dev.syn()

    def key_down(self, key: str):
        self._emit_key(self.kbd, KEYS[key], 1)

    def key_up(self, key: str):
        self._emit_key(self.kbd, KEYS[key], 0)

    def tap(self, key: str, hold: float = 0.06, wait: float = 0.15):
        self.key_down(key)
        time.sleep(hold)
        self.key_up(key)
        time.sleep(wait)

    def hold(self, key: str, duration: float):
        self.key_down(key)
        time.sleep(duration)
        self.key_up(key)

    def type_text(self, text: str, delay: float = 0.05):
        for ch in text:
            code, shift = DE_CHARMAP[ch]
            if shift:
                self._emit_key(self.kbd, e.KEY_LEFTSHIFT, 1)
                time.sleep(0.01)
            self._emit_key(self.kbd, code, 1)
            time.sleep(0.02)
            self._emit_key(self.kbd, code, 0)
            if shift:
                time.sleep(0.01)
                self._emit_key(self.kbd, e.KEY_LEFTSHIFT, 0)
            time.sleep(delay)

    # --- mouse ------------------------------------------------------------
    def click(self, button: str = "left", wait: float = 0.2):
        btn = {"left": e.BTN_LEFT, "right": e.BTN_RIGHT, "middle": e.BTN_MIDDLE}[button]
        self._emit_key(self.mouse, btn, 1)
        time.sleep(0.08)
        self._emit_key(self.mouse, btn, 0)
        time.sleep(wait)

    def double_click(self, wait: float = 0.2):
        """Fast double-click (inside Minecraft's ~250ms list threshold)."""
        for _ in range(2):
            self._emit_key(self.mouse, e.BTN_LEFT, 1)
            time.sleep(0.04)
            self._emit_key(self.mouse, e.BTN_LEFT, 0)
            time.sleep(0.06)
        time.sleep(wait)

    def button_down(self, button: str = "left"):
        btn = {"left": e.BTN_LEFT, "right": e.BTN_RIGHT}[button]
        self._emit_key(self.mouse, btn, 1)

    def button_up(self, button: str = "left"):
        btn = {"left": e.BTN_LEFT, "right": e.BTN_RIGHT}[button]
        self._emit_key(self.mouse, btn, 0)

    def move_rel(self, dx: int, dy: int, steps: int = 20, step_delay: float = 0.01):
        """Smooth relative motion — what a pointer-locked game camera sees."""
        sx = dx / steps
        sy = dy / steps
        ax = ay = 0.0
        for _ in range(steps):
            ax += sx
            ay += sy
            ix, iy = int(round(ax)), int(round(ay))
            if ix or iy:
                if ix:
                    self.mouse.write(e.EV_REL, e.REL_X, ix)
                if iy:
                    self.mouse.write(e.EV_REL, e.REL_Y, iy)
                self.mouse.syn()
                ax -= ix
                ay -= iy
            time.sleep(step_delay)

    def scroll(self, clicks: int):
        step = 1 if clicks > 0 else -1
        for _ in range(abs(clicks)):
            self.mouse.write(e.EV_REL, e.REL_WHEEL, step)
            self.mouse.syn()
            time.sleep(0.05)
