from typing import List, Dict, TypeVar, Generic, Tuple
from abc import ABC, abstractmethod
import os

ESCAPE_CODE = "\x1b["
END_CODE = "m"
JOIN_CODE = ";"


class ShowCode:
    code: str

    def __init__(self, code: str):
        self.code = code

    def __str__(self) -> str:
        return f"\\033[{self.code}{END_CODE}"

    def __repr__(self) -> str:
        return f"\\033{self.code}{END_CODE}"

    def to_ansi(self) -> str:
        return f"{ESCAPE_CODE}{self.code}{END_CODE}"


RESET_CODE = ShowCode("0")


class Section:
    name: str
    table: str

    def __init__(self, name: str, table: str):
        self.name = name
        self.table = table

    def str(self) -> str:
        return f"{TEXT_STYLES.bold.to_ansi()}{self.name}{RESET_CODE.to_ansi()}:\n{self.table}"


N = TypeVar("N")


class CodesBase(ABC, Generic[N]):
    title: str
    table_attrs: Dict[str, N]

    def __init__(self, title: str, table_attrs: Dict[str, N]):
        self.title = title
        self.table_attrs = table_attrs

    @abstractmethod
    def to_ansi(self, name: N):
        pass

    @abstractmethod
    def get(self, name: N):
        pass

    def table(self) -> str:
        max_len: int = max([len(key) for key in self.table_attrs.keys()]) + 2
        arr: List[str] = []
        for key, value in self.table_attrs.items():
            padding = " " * (max_len - len(key))
            arr.append(
                f"{self.to_ansi(value)}{key}{RESET_CODE.to_ansi()}:{padding}{getattr(self, str(value))}"
            )
        return "\n".join(arr)

    def section(self) -> Section:
        return Section(
            name=self.title,
            table=self.table(),
        )


class TextStyles(CodesBase[str]):
    bold: ShowCode = ShowCode("1")
    dim: ShowCode = ShowCode("2")
    italic: ShowCode = ShowCode("3")
    underline: ShowCode = ShowCode("4")
    blink: ShowCode = ShowCode("5")
    reverse: ShowCode = ShowCode("7")
    hidden: ShowCode = ShowCode("8")
    strikethrough: ShowCode = ShowCode("9")

    def __init__(self):
        table_attrs = {
            "Bold": "bold",
            "Dim": "dim",
            "Italic": "italic",
            "Underline": "underline",
            "Blink": "blink",
            "Reverse": "reverse",
            "Hidden": "hidden",
            "Strikethrough": "strikethrough",
        }
        super().__init__("Text Styles", table_attrs)

    def to_ansi(self, style_name: str) -> str:
        return getattr(self, style_name).to_ansi()

    def get(self, style_name: str) -> str:
        return str(getattr(self, style_name))


class AnsiColors(CodesBase[str]):
    black: ShowCode
    red: ShowCode
    green: ShowCode
    yellow: ShowCode
    blue: ShowCode
    magenta: ShowCode
    cyan: ShowCode
    white: ShowCode

    def __init__(self, title: str, start: int):
        self.title = title
        self.black = ShowCode(str(start))
        self.red = ShowCode(str(start + 1))
        self.green = ShowCode(str(start + 2))
        self.yellow = ShowCode(str(start + 3))
        self.blue = ShowCode(str(start + 4))
        self.magenta = ShowCode(str(start + 5))
        self.cyan = ShowCode(str(start + 6))
        self.white = ShowCode(str(start + 7))
        table_attrs = {
            "Black": "black",
            "Red": "red",
            "Green": "green",
            "Yellow": "yellow",
            "Blue": "blue",
            "Magenta": "magenta",
            "Cyan": "cyan",
            "White": "white",
        }
        super().__init__(title, table_attrs)

    def to_ansi(self, color_name: str) -> str:
        return getattr(self, color_name).to_ansi()

    def get(self, color_name: str) -> str:
        return str(getattr(self, color_name))


class FullAnsiColor(CodesBase[int]):
    code1: str
    code2: str
    start: int
    end: int
    max_len: int = 0

    def __init__(self, title: str, code1: str, code2: str, start: int, end: int):
        self.code1 = code1
        self.code2 = code2
        self.start = start
        self.end = end
        self.max_len = len(str(self.end))
        table_attrs = {str(i): i for i in range(self.start, self.end + 1)}
        super().__init__(title, table_attrs)

    def __str__(self) -> str:
        return f"\\033[{self.code1};{self.code2};<index>{END_CODE}"

    def __repr__(self) -> str:
        return f"\\033[{self.code1};{self.code2};<index>{END_CODE}"

    def code(self, index: int) -> ShowCode:
        if index < self.start or index > self.end:
            raise ValueError("Index out of range for the specified ANSI color codes.")
        codes = [self.code1, self.code2, str(index)]
        return ShowCode(JOIN_CODE.join(codes))

    def to_ansi(self, index: int) -> str:
        return self.code(index).to_ansi()

    def get(self, index: int) -> str:
        return str(self.code(index))

    def table(self) -> str:
        colors = []
        term_width = os.get_terminal_size().columns - 4
        cols = term_width // (self.max_len + 1)
        for i in range(self.start, self.end + 1):
            end = RESET_CODE.to_ansi()
            if i % cols == 0 and i != self.start:
                end = f"{RESET_CODE.to_ansi()}\n"
            color_code = self.to_ansi(i)
            padded_index = self.pad(str(i))
            colors.append(f"{color_code}{padded_index}{end}")
        return " ".join(colors)

    def pad(self, text: str) -> str:
        padding = self.max_len - len(text)
        front_pad = padding // 2
        back_pad = padding - front_pad
        front = " " * front_pad
        back = " " * back_pad
        return front + text + back


class RGBColor(CodesBase[Tuple[int, int, int]]):
    code1: str
    code2: str

    def __init__(self, title: str, code1: str, code2: str):
        self.code1 = code1
        self.code2 = code2
        table_attrs = {
            "RGB": (127, 255, 0),
        }
        super().__init__(title, table_attrs)

    def __str__(self) -> str:
        return f"\\033[{self.code1};{self.code2};<r>;<g>;<b>{END_CODE}"

    def __repr__(self) -> str:
        return f"\\033[{self.code1};{self.code2};<r>;<g>;<b>{END_CODE}"

    def code(self, color: Tuple[int, int, int]) -> ShowCode:
        if not all(0 <= val <= 255 for val in color):
            raise ValueError("RGB values must be in the range 0-255.")
        codes = [self.code1, self.code2, str(color[0]), str(color[1]), str(color[2])]
        return ShowCode(JOIN_CODE.join(codes))

    def to_ansi(self, color: Tuple[int, int, int]) -> str:
        return self.code(color).to_ansi()

    def get(self, color: Tuple[int, int, int]) -> str:
        return str(self.code(color))

    def table(self) -> str:
        return f"{self}"


FOREGROUND_COLORS = AnsiColors(title="Foreground ANSI Colors", start=30)
BACKGROUND_COLORS = AnsiColors(title="Background ANSI Colors", start=40)
BRIGHT_FOREGROUND_COLORS = AnsiColors(title="Foreground Bright ANSI Colors", start=90)
BRIGHT_BACKGROUND_COLORS = AnsiColors(title="Background Bright ANSI Colors", start=100)
FULL_FOREGROUND_COLOR = FullAnsiColor(
    title="Foreground 256 ANSI Colors", code1="38", code2="5", start=0, end=255
)
FULL_BACKGROUND_COLOR = FullAnsiColor(
    title="Background 256 ANSI Colors", code1="48", code2="5", start=0, end=255
)
RGB_FOREGROUND_COLOR = RGBColor(title="Foreground RGB Colors", code1="38", code2="2")
RGB_BACKGROUND_COLOR = RGBColor(title="Background RGB Colors", code1="48", code2="2")
TEXT_STYLES = TextStyles()


class ColorTypes:
    base: AnsiColors
    bright: AnsiColors
    full: FullAnsiColor
    rgb: RGBColor

    def __init__(
        self,
        base: AnsiColors,
        bright: AnsiColors,
        full: FullAnsiColor,
        rgb: RGBColor,
    ):
        self.base = base
        self.bright = bright
        self.full = full
        self.rgb = rgb


class AnsiCodes:
    foreground: ColorTypes = ColorTypes(
        base=FOREGROUND_COLORS,
        bright=BRIGHT_FOREGROUND_COLORS,
        full=FULL_FOREGROUND_COLOR,
        rgb=RGB_FOREGROUND_COLOR,
    )
    background: ColorTypes = ColorTypes(
        base=BACKGROUND_COLORS,
        bright=BRIGHT_BACKGROUND_COLORS,
        full=FULL_BACKGROUND_COLOR,
        rgb=RGB_BACKGROUND_COLOR,
    )
    text_styles: TextStyles = TEXT_STYLES
    escape_codes: str = "\n".join(
        [
            "Key         ^[",
            "Octal       \\033",
            "Hexadecimal \\x1b",
            "Unicode     \\u001b",
            "Decimal      27",
        ]
    )

    def show_all(self) -> str:
        sections: List[Section] = [
            Section(
                name="Escape Codes",
                table=self.escape_codes,
            ),
            Section(
                name="Join Code",
                table=f"The character '{JOIN_CODE}' is used to separate multiple codes in a single ANSI sequence.",
            ),
            Section(
                name="Reset Code",
                table=str(RESET_CODE),
            ),
            self.text_styles.section(),
            self.foreground.base.section(),
            self.background.base.section(),
            self.foreground.bright.section(),
            self.background.bright.section(),
            self.foreground.full.section(),
            self.background.full.section(),
        ]
        output = [s.str() for s in sections]
        return "\n\n".join(output)
