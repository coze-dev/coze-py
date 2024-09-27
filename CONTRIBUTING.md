## Setting up the environment

create a virtual environment:

```shell
python -m venv ./.venv
```

active the virtual environment:

```shell
source ./.venv/bin/activate
```

We use [Poetry](https://python-poetry.org/) to manage dependencies, you can install it by:

```shell
python -m pip install poetry 
```

And then install dependencies:

```shell
poetry install
```

## Pre Commit

```shell
pre-commit install
```