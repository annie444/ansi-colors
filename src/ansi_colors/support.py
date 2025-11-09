from __future__ import annotations

from typing import List, Pattern
from enum import Enum
import os
import sys
import re
import platform
from ansi_colors.utils import warn, debug, info
from functools import lru_cache


class ColorSupport(Enum):
    NO_COLOR = 0
    BASIC = 1
    EXTENDED = 2
    TRUECOLOR = 3

    def __str__(self) -> str:
        name: str = ""
        match self:
            case ColorSupport.NO_COLOR:
                name = "No Color Support"
            case ColorSupport.BASIC:
                name = "Basic Color Support (16 colors)"
            case ColorSupport.EXTENDED:
                name = "Extended Color Support (256 colors)"
            case ColorSupport.TRUECOLOR:
                name = "True Color Support (16 million colors)"
        return name

    def __repr__(self) -> str:
        return self.__str__()


TRUE_COLOR_TERMS: List[str] = [
    "iterm",
]

TRUE_COLOR_TERMS_RE: List[Pattern] = [
    re.compile(r"vte.*"),
    re.compile(r".*-truecolor"),
]

WINDOWS_TRUE_COLOR_TERMS: List[str] = [
    "pwsh",
    "winterm",
]

WINDOWS_TRUE_COLOR_TERMS_RE: List[Pattern] = [
    re.compile(r"windows terminal.*"),
    re.compile(r"windows powershell.*"),
    re.compile(r"windows cmd.*"),
    re.compile(r"cmd.*"),
    re.compile(r"powershell.*"),
    re.compile(r"wt.*"),
    re.compile(r"pwsh.*"),
]

TRUE_COLOR_TERM_PROGRAMS: List[str] = [
    "alacritty",
    "conemu",
    "conhost",
    "connectbot",
    "contour",
    "finalterm",
    "foot",
    "ghostty",
    "hterm",
    "kitty",
    "konsole",
    "macterm",
    "mintty",
    "mobaxterm",
    "mosh",
    "xshell",
    "pangoterm",
    "putty",
    "qterminal",
    "st",
    "teraterm",
    "bobcat",
    "termux",
    "therm",
    "upterm",
    "warp",
    "wezterm",
    "xst",
    "xterm",
    "evilvte",
    "guake",
    "lilyterm",
    "lxterminal",
    "pantheon",
    "roxterm",
    "sakura",
    "terminator",
    "termit",
    "termite",
    "tilda",
    "tilix",
    "tinyterm",
    "xfce4",
    "xterm.js",
    "tabby",
    "vscode",
    "zoc",
]

TRUE_COLOR_TERM_PROGRAMS_RE: List[Pattern] = [
    re.compile(r"black.*"),
    re.compile(r".*retro.*"),
    re.compile(r"iterm2.*"),
    re.compile(r"gnome.*"),
    re.compile(r"hyper.*"),
]


def match(name: str, strs: List[str], patterns: List[Pattern]) -> bool:
    if name.lower() in strs:
        return True
    for pattern in patterns:
        if pattern.match(name):
            return True
    return False


@lru_cache()
def supports_color() -> ColorSupport:
    """
    Returns True if the running system's terminal supports color, and False otherwise.
    """
    plat = sys.platform
    plat_name = platform.system().lower()
    support = ColorSupport.NO_COLOR
    if not hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        warn("Standard output is not a TTY. Disabling color support.")
        return support
    if plat == "Pocket PC" and (plat == "win32" and "ANSICON" not in os.environ):
        info("Pocket PC detected without ANSICON. Disabling color support.")
        return support
    elif plat == "win32" and "ANSICON" in os.environ:
        info("ANSICON detected on Windows. Enabling basic color support.")
        support = ColorSupport.BASIC
    else:
        term_program = os.environ.get("TERM_PROGRAM", "").lower()
        term = os.environ.get("TERM", "").lower()
        colorterm = os.environ.get("COLORTERM", "").lower()
        if (
            colorterm in ("truecolor", "24bit")
            or (
                plat_name == "windows"
                and match(
                    term_program,
                    WINDOWS_TRUE_COLOR_TERMS,
                    WINDOWS_TRUE_COLOR_TERMS_RE,
                )
            )
            or (
                plat_name != "windows"
                and match(
                    term_program,
                    TRUE_COLOR_TERM_PROGRAMS,
                    TRUE_COLOR_TERM_PROGRAMS_RE,
                )
            )
        ):
            debug("True color support detected.")
            support = ColorSupport.TRUECOLOR
        elif "WT_SESSION" in os.environ or match(
            term, TRUE_COLOR_TERMS, TRUE_COLOR_TERMS_RE
        ):
            debug("Full color support detected.")
            support = ColorSupport.EXTENDED

    return support
