## Setting up the environment

create a virtual environment:

```shell
python -m venv ./.venv
```

active the virtual environment:

```shell
source ./.venv/bin/activate
```

We use [uv](https://docs.astral.sh/uv/) to manage dependencies, you can install it by:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

And then install dependencies:

```shell
uv sync --all-extras
```

## Pre Commit

```shell
pre-commit install
```
