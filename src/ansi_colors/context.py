from __future__ import annotations

import typing as t
import rich_click as click
from ansi_colors.codes import AnsiCodes, ColorTypes
from threading import local
from functools import update_wrapper

if t.TYPE_CHECKING:
    import typing_extensions as te

    P = te.ParamSpec("P")

R = t.TypeVar("R")
T = t.TypeVar("T")
_AnyCallable = t.Callable[..., t.Any]

_local = local()


class ColorContext:
    codes: AnsiCodes

    def __init__(self):
        self.codes = AnsiCodes()
        self._section = ""

    @property
    def section(self) -> ColorTypes:
        return getattr(self.codes, self._section)

    @section.setter
    def section(self, value: str):
        self._section = value


def pass_context(
    f: t.Callable[te.Concatenate[click.Context, ColorContext, P], R],
) -> t.Callable[P, R]:
    @click.pass_context
    def new_func(ctx: click.Context, *args: P.args, **kwargs: P.kwargs) -> R:
        if not isinstance(ctx.obj, ColorContext):
            ctx.obj = ColorContext()
        return ctx.invoke(f, ctx, ctx.obj, *args, **kwargs)

    return update_wrapper(new_func, f)


def pass_obj(
    f: t.Callable[te.Concatenate[ColorContext, P], R],
) -> t.Callable[P, R]:
    @click.pass_context
    def new_func(ctx: click.Context, *args: P.args, **kwargs: P.kwargs) -> R:
        if not isinstance(ctx.obj, ColorContext):
            ctx.obj = ColorContext()
        return ctx.invoke(f, ctx.obj, *args, **kwargs)

    return update_wrapper(new_func, f)


def color_args(f):
    @click.argument(
        "color",
        type=click.Choice(
            [
                "black",
                "red",
                "green",
                "yellow",
                "blue",
                "magenta",
                "cyan",
                "white",
            ],
            case_sensitive=False,
        ),
        default=None,
        required=False,
    )
    def new_func(
        color: t.Optional[str] = None,
        *args,
        **kwargs,
    ):
        return f(color=color, *args, **kwargs)

    return update_wrapper(new_func, f)


def rgb_args(f):
    @click.argument(
        "red",
        type=click.IntRange(0, 255),
        default=None,
        required=False,
    )
    @click.argument(
        "green",
        type=click.IntRange(0, 255),
        default=None,
        required=False,
    )
    @click.argument(
        "blue",
        type=click.IntRange(0, 255),
        default=None,
        required=False,
    )
    def new_func(
        red: t.Optional[int] = None,
        green: t.Optional[int] = None,
        blue: t.Optional[int] = None,
        *args,
        **kwargs,
    ):
        return f(red=red, green=green, blue=blue, *args, **kwargs)

    return update_wrapper(new_func, f)
