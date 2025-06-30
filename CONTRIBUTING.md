## Setting up the environment

We use [uv](https://docs.astral.sh/uv/) to manage dependencies, you can install it by:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

And then install dependencies:

```shell
uv sync
```

## Pre Commit

```shell
uv run pre-commit install
```
