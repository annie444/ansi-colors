from __future__ import annotations

import typing as t
import rich_click as click
from ansi_colors.context import (
    ColorContext,
    pass_context,
    color_args,
    rgb_args,
    pass_obj,
)
from ansi_colors.utils import debug, get_log_level, set_log_level, LogLevel


@click.group("ansi-colors", invoke_without_command=True)
@click.option(
    "-q",
    "--quiet",
    count=True,
    help="Decrease the verbosity level",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase the verbosity level",
)
@pass_context
def main(
    ctx: click.Context,
    codes: ColorContext,
    quiet: int,
    verbose: int,
):
    """ANSI Color Codes CLI Tool"""
    # Start from INFO and walk the level up/down based on `-v` and `-q` counts.
    quiet = quiet or 0
    verbose = verbose or 0
    level_value = get_log_level().value + verbose - quiet
    level_value = max(LogLevel.NO_LOG.value, min(LogLevel.DEBUG.value, level_value))

    set_log_level(LogLevel(level_value))
    debug(f"ansi-colors {ctx.invoked_subcommand}")
    if ctx.invoked_subcommand is None:
        click.echo(codes.codes.show_all())


@main.command("styles")
@click.argument(
    "style",
    type=click.Choice(
        [
            "reset",
            "bold",
            "dim",
            "italic",
            "underline",
            "blink",
            "reverse",
            "hidden",
            "strikethrough",
        ],
        case_sensitive=False,
    ),
    required=False,
    default=None,
)
@pass_obj
def styles(codes: ColorContext, style: t.Optional[str]):
    """Display text style codes"""
    debug(f"ansi-colors styles {style}")
    if style:
        click.echo(codes.codes.text_styles.to_ansi(style))
    else:
        click.echo(codes.codes.text_styles.section().str())


@main.group("fg", invoke_without_command=True)
@pass_context
def fg(ctx: click.Context, codes: ColorContext):
    """Display foreground color codes"""
    debug(f"ansi-colors fg {ctx.invoked_subcommand}")
    codes.section = "foreground"
    if ctx.invoked_subcommand is None:
        click.echo(codes.section.show_all())


@main.group("bg", invoke_without_command=True)
@pass_context
def bg(ctx: click.Context, codes: ColorContext):
    """Display background color codes"""
    debug(f"ansi-colors bg {ctx.invoked_subcommand}")
    codes.section = "background"
    if ctx.invoked_subcommand is None:
        click.echo(codes.section.show_all())


def base_callback(codes: ColorContext, color: t.Optional[str]):
    """Display base background color codes"""
    if color:
        click.echo(codes.section.base.to_ansi(color))
    else:
        click.echo(codes.section.base.section().str())


@fg.command("base")
@color_args
@pass_obj
def fg_base(codes: ColorContext, color: t.Optional[str]):
    """Display base foreground color codes"""
    base_callback(codes, color)


@bg.command("base")
@color_args
@pass_obj
def bg_base(codes: ColorContext, color: t.Optional[str]):
    """Display base background color codes"""
    base_callback(codes, color)


def bright_callback(codes: ColorContext, color: t.Optional[str]):
    """Display bright color codes"""
    if color is not None:
        click.echo(codes.section.bright.to_ansi(color))
    else:
        click.echo(codes.section.bright.section().str())


@fg.command("bright")
@color_args
@pass_obj
def fg_bright(codes: ColorContext, color: t.Optional[str]):
    """Display bright foreground color codes"""
    bright_callback(codes, color)


@bg.command("bright")
@color_args
@pass_obj
def bg_bright(codes: ColorContext, color: t.Optional[str]):
    """Display bright background color codes"""
    bright_callback(codes, color)


def full_callback(codes: ColorContext, index: t.Optional[int]):
    """Display full background color codes"""
    if index is not None:
        click.echo(codes.section.full.to_ansi(index))
    else:
        click.echo(codes.section.full.section().str())


@fg.command("full")
@click.argument(
    "index",
    type=click.IntRange(0, 255),
    default=None,
    required=False,
)
@pass_obj
def fg_full(codes: ColorContext, index: t.Optional[int]):
    """Display full foreground color codes"""
    full_callback(codes, index)


@bg.command("full")
@click.argument(
    "index",
    type=click.IntRange(0, 255),
    default=None,
    required=False,
)
@pass_obj
def bg_full(codes: ColorContext, index: t.Optional[int]):
    """Display full foreground color codes"""
    full_callback(codes, index)


def rgb_callback(
    codes: ColorContext,
    red: t.Optional[int],
    green: t.Optional[int],
    blue: t.Optional[int],
):
    """Display background color codes"""
    if red is not None and green is not None and blue is not None:
        click.echo(codes.section.rgb.to_ansi((red, green, blue)))
    else:
        click.echo(codes.section.rgb.section().str())


@fg.command("rgb")
@rgb_args
@pass_obj
def fg_rgb(
    codes: ColorContext,
    red: t.Optional[int],
    green: t.Optional[int],
    blue: t.Optional[int],
):
    """Display foreground RGB color codes"""
    rgb_callback(codes, red, green, blue)


@fg.command("rgb")
@rgb_args
@pass_obj
def bg_rgb(
    codes: ColorContext,
    red: t.Optional[int],
    green: t.Optional[int],
    blue: t.Optional[int],
):
    """Display background RGB color codes"""
    rgb_callback(codes, red, green, blue)
