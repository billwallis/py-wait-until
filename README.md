<span align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![tests](https://github.com/billwallis/py-wait-until/actions/workflows/tests.yaml/badge.svg)](https://github.com/billwallis/py-wait-until/actions/workflows/tests.yaml)
[![coverage](https://raw.githubusercontent.com/billwallis/py-wait-until/refs/heads/main/coverage.svg)](https://github.com/dbrgn/coverage-badge)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/billwallis/py-wait-until/main.svg)](https://results.pre-commit.ci/latest/github/billwallis/py-wait-until/main)
[![GitHub last commit](https://img.shields.io/github/last-commit/billwallis/py-wait-until)](https://shields.io/badges/git-hub-last-commit)

</span>

---

# Wait Until

Print a loading spinner while another command is running.

## Usage

`py-wait-until` is a CLI tool which runs a command and displays a loading spinner while the command is executing.

The easiest way to use `py-wait-until` is via [`uvx`](https://docs.astral.sh/uv/guides/tools/), for example:

```shell
uvx py-wait-until python -c "import time; time.sleep(2)"
```

Alternatively, install from PyPI and run without `uvx`:

```shell
pip install py-wait-until
py-wait-until python -c "import time; time.sleep(2)"
```

The return code of the original command is preserved. Specifying no command will exit with code 1 and show the help message.

## Contributing

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and then install the dependencies:

```bash
uvx --from poethepoet poe install
```
