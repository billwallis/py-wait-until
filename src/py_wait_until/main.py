import argparse
import enum
import random
import subprocess
import sys
import time
from collections.abc import Generator, Sequence
from typing import TextIO

WAIT_DURATION_SECONDS = 0.1
ANSI_CLEAR_LINE = "\033[2K"
ANSI_HIDE_CURSOR = "\033[?25l"
ANSI_SHOW_CURSOR = "\033[?25h"


class Spinner(enum.StrEnum):
    LINE = "line"
    DOTS = "dots"
    SAND = "sand"

    def chars(self) -> Sequence[str]:
        return {
            # Basic/simple option
            self.LINE: ["|", "/", "-", "\\"],
            # Inspired by Docker and dbt Fusion's loading indicator
            self.DOTS: [
                *["⠄", "⠆", "⠖", "⠶", "⠲", "⠰"],
                *["⠠", "⠤", "⠦", "⠶", "⠖", "⠒"],
                *["⠐", "⠰", "⠴", "⠶", "⠦", "⠆"],
                *["⠂", "⠒", "⠲", "⠶", "⠴", "⠤"],
            ],
            # https://stackoverflow.com/a/12305221/8213085
            # https://raw.githubusercontent.com/sindresorhus/cli-spinners/master/spinners.json
            self.SAND: [
                *["⠁", "⠂", "⠄", "⡀", "⡈", "⡐", "⡠", "⣀"],
                *["⣁", "⣂", "⣄", "⣌", "⣔", "⣤", "⣥", "⣦"],
                *["⣮", "⣶", "⣷", "⣿", "⡿", "⠿", "⢟", "⠟"],
                *["⡛", "⠛", "⠫", "⢋", "⠋", "⠍", "⡉", "⠉"],
                *["⠑", "⠡", "⢁"],
            ],
        }[self]


def _write_line(stream: TextIO, message: str) -> None:
    """
    Write and flush a line to the given stream.
    """

    stream.write(message)
    stream.flush()


def _spinner(chars: Sequence[str]) -> Generator[str]:
    """
    Return an infinite generator that yields spinner characters.
    """

    index = -1
    while True:
        index += 1
        yield chars[index % len(chars)]


def _wait_for_process(
    cmd: list[str],
    message: str,
    spinner: Spinner,
) -> int:
    """
    Execute a command and display a waiting message until it completes.
    """

    # Only show spinner if stdout is a TTY (interactive terminal)
    if is_tty := sys.stdout.isatty():
        _write_line(sys.stdout, ANSI_HIDE_CURSOR)

    process = subprocess.Popen(  # noqa: S603
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    spin = _spinner(spinner.chars())
    while process.poll() is None:
        if is_tty:
            _write_line(
                sys.stdout,
                f"\r{message} {next(spin)}",
            )
        time.sleep(WAIT_DURATION_SECONDS)

    if is_tty:
        _write_line(sys.stdout, f"\r{ANSI_CLEAR_LINE}")
        _write_line(sys.stdout, ANSI_SHOW_CURSOR)

    stdout, stderr = process.communicate()
    if stdout:
        _write_line(sys.stdout, stdout)
    if stderr:
        _write_line(sys.stderr, stderr)

    return process.returncode


def main(argv: Sequence[str] | None = None) -> int:
    """
    Print a loading spinner while another process is running.
    """

    parser = argparse.ArgumentParser(
        description="Print a loading spinner while another command is running.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command(s) to execute",
    )
    parser.add_argument(
        "-m",
        "--message",
        type=str,
        required=False,
        default="Waiting for process to finish...",
        help="Message to display while waiting",
    )
    spinners = ", ".join([f"'{s}'" for s in Spinner])
    parser.add_argument(
        "--spinner",
        type=Spinner,
        required=False,
        help=f"The spinner to display ({spinners}). Defaults to a randomly chosen one",
        default=random.choice([s for s in Spinner]),  # noqa: S311
    )

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    return _wait_for_process(
        cmd=args.command,
        message=args.message,
        spinner=args.spinner,
    )


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
