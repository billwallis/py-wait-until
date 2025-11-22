import argparse
import contextlib
import subprocess
import sys
import time
from collections.abc import Generator, Sequence
from typing import TextIO

WAIT_DURATION_SECONDS = 0.1
ANSI_CLEAR_LINE = "\033[2K"
ANSI_HIDE_CURSOR = "\033[?25l"
ANSI_SHOW_CURSOR = "\033[?25h"


def _write_line(stream: TextIO, message: str) -> None:
    """
    Write and flush a line to the given stream.
    """

    stream.write(message)
    stream.flush()


@contextlib.contextmanager
def _hide_cursor() -> Generator[None]:
    """
    Context manager to hide the terminal cursor.
    """

    _write_line(sys.stdout, ANSI_HIDE_CURSOR)
    yield
    _write_line(sys.stdout, ANSI_SHOW_CURSOR)


def _spinner() -> Generator[str]:
    """
    Return an infinite generator that yields spinner characters.
    """

    chars = ["|", "/", "-", "\\"]
    index = -1
    while True:
        index += 1
        yield chars[index % len(chars)]


def _wait_for_process(cmd: list[str]) -> int:
    """
    Execute a command and display a waiting message until it completes.
    """

    # Only show spinner if stdout is a TTY (interactive terminal)
    is_tty = sys.stdout.isatty()

    process = subprocess.Popen(  # noqa: S603
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    spin = _spinner()
    while process.poll() is None:
        if is_tty:
            _write_line(
                sys.stdout,
                f"\rWaiting for process to finish... {next(spin)}",
            )
        time.sleep(WAIT_DURATION_SECONDS)

    if is_tty:
        _write_line(sys.stdout, f"\r{ANSI_CLEAR_LINE}")

    stdout, stderr = process.communicate()
    if stdout:
        _write_line(sys.stdout, stdout)
    if stderr:
        _write_line(sys.stderr, stderr)

    return process.returncode


def main(argv: Sequence[str] | None = None) -> int:
    """
    Wait until a command completes.
    """

    parser = argparse.ArgumentParser(
        description="Wait until a command completes.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command and arguments to execute",
    )

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    with _hide_cursor():
        return _wait_for_process(args.command)


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
