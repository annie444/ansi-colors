import rich_click as click
from ansi_colors.codes import AnsiCodes


@click.command("ansi-colors")
def main():
    print(AnsiCodes().show_all())
