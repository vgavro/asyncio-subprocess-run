# asyncio-subprocess-run

This is asyncio drop-in replacement for `subprocess.run`, which is expected to be in `asyncio.subprocess.run`, but it isn't.

For documentation see [https://docs.python.org/3/library/subprocess.html#subprocess.run](https://docs.python.org/3/library/subprocess.html#subprocess.run)

## Install

```sh
pip3 install asyncio-subprocess-run
```

## Usage

```python3
from asyncio_subprocess_run import run


async def get_uid():
    return int(
        (await run(['id', '-u'], check=True, text=True, capture_output=True))
        .stdout.strip())
```
