import pathlib
import subprocess
from collections.abc import Sequence

import pytest

from src.py_wait_until.main import main

QAPLA = "Qapla'!"


def python(cmd: str) -> Sequence[str]:
    return ["python", "-c", cmd]


def echo(message: str) -> Sequence[str]:
    return python(f"print({message!r})")


def test__cli_can_be_invoked() -> None:
    """
    The CLI can be invoked without error when given a command.
    """

    assert subprocess.call(["py-wait-until", *echo(QAPLA)]) == 0  # noqa: S603, S607


def test__cli_with_no_arguments_prints_help(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    The CLI prints help when called with no command.
    """

    with monkeypatch.context() as m:
        m.setattr("sys.argv", ["py-wait-until"])
        assert main() == 1

    assert capsys.readouterr().out.startswith("usage:")


def test__successful_process_returns_zero(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    A successful command returns exit code 0.
    """

    monkeypatch.setattr("sys.stdout.isatty", lambda: True)

    assert main(echo(QAPLA)) == 0
    assert QAPLA in capsys.readouterr().out


def test__unsuccessful_command_returns_non_zero() -> None:
    """
    A command which exits with a non-zero code returns that code.
    """

    assert main(python("import sys; sys.exit(3)")) == 3


def test__raised_exceptions_are_propagated() -> None:
    """
    Exceptions raised by the subprocess are propagated.
    """

    with pytest.raises(Exception) as exception:
        # This should raise a `FileNotFoundError` on macOS
        main(["something", "broken"])

    assert exception.value != 0


def test__spinner_shows_in_tty_mode(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    The spinner is shown when stdout is a TTY.
    """

    monkeypatch.setattr("sys.stdout.isatty", lambda: True)

    assert main(echo(QAPLA)) == 0
    assert QAPLA in capsys.readouterr().out


def test__spinner_shows_in_tty_mode_with_custom_message(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    A custom message can be shown with the spinner.
    """

    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    message = "Custom waiting message"

    assert main(["-m", message, *echo(QAPLA)]) == 0
    assert message in capsys.readouterr().out

    assert main(["--message", message, *echo(QAPLA)]) == 0
    assert message in capsys.readouterr().out


def test__stderr_output_is_captured(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Stderr from the subprocess is captured and displayed.
    """

    cmd = "import sys; sys.stderr.write('error message\\n')"

    assert main(python(cmd)) == 0
    assert capsys.readouterr().err == "error message\n"


def test__written_file_does_not_include_ansi_codes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
) -> None:
    """
    A file written by the subprocess does not include ANSI codes.
    """

    monkeypatch.setattr("sys.stdout.isatty", lambda: True)

    file = tmp_path / "output.txt"
    file.touch(exist_ok=True)
    file_path = str(file.resolve())
    cmd = "; ".join(
        [
            "import os",
            f"f = open({file_path!r}, 'w')",
            "f.write('bish bash bosh\\n')",
            "f.close()",
        ]
    )

    assert main(python(cmd)) == 0
    assert file.read_text() == "bish bash bosh\n"
