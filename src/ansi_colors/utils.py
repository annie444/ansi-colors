from __future__ import annotations

from enum import IntEnum
from rich.console import Console

console = Console(soft_wrap=True)
msgs = []


class LogLevel(IntEnum):
    NO_LOG = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4


class LogStore:
    _instance = None  # Class-level attribute to store the single instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:  # If no instance exists, create one
            cls._instance = super().__new__(cls)
        return cls._instance  # Always return the existing instance

    def __init__(self, value):
        # This __init__ method will be called every time a new "instance" is requested,
        # even though only one actual object is created.
        # Be careful with initialization logic here if you only want it to run once.
        if not hasattr(self, "_initialized"):  # Prevent re-initialization
            self.value = value
            self._initialized = True

    def set_level(self, value: LogLevel) -> None:
        self.value = value


global log_level
log_level = LogStore(LogLevel.WARNING)


def get_log_level() -> LogLevel:
    return log_level.value


def set_log_level(level: LogLevel) -> None:
    log_level.set_level(level)


def warn(message: str) -> None:
    """Display a warning message to the user.

    Args:
        message (str): The warning message to display.
    """
    if message in msgs or log_level.value <= LogLevel.WARNING:
        return
    console.log(f"[bold yellow]Warning:[/bold yellow] {message}")
    msgs.append(message)


def info(message: str) -> None:
    """Display an informational message to the user.

    Args:
        message (str): The informational message to display.
    """
    if message in msgs or log_level.value <= LogLevel.INFO:
        return
    console.log(f"[bold blue]Info:[/bold blue] {message}")
    msgs.append(message)


def error(message: str) -> None:
    """Display an error message to the user.

    Args:
        message (str): The error message to display.
    """
    if message in msgs or log_level.value <= LogLevel.ERROR:
        return
    console.log(f"[bold red]Error:[/bold red] {message}")
    msgs.append(message)


def debug(message: str) -> None:
    """Display a debug message to the user.

    Args:
        message (str): The debug message to display.
    """
    if message in msgs or log_level.value <= LogLevel.DEBUG:
        return
    console.log(f"[dim][cyan]Debug:[/cyan] {message}[/dim]")
    msgs.append(message)
