import asyncio
from subprocess import PIPE, TimeoutExpired, CalledProcessError, CompletedProcess
import io
import locale


async def run(args, input=None, capture_output=False, shell=False, timeout=None,
              check=False, encoding=None, errors=None, text=None,
              universal_newlines=None, **kwargs):

    text = encoding or errors or text or universal_newlines
    # universal_newlines is deprecated, use text instead
    if text and not encoding:
        encoding = locale.getpreferredencoding()

    if input is not None:
        if kwargs.get('stdin') is not None:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = PIPE
        if text:
            input = input.encode(encoding, errors)

    if capture_output:
        if kwargs.get('stdout') is not None or kwargs.get('stderr') is not None:
            raise ValueError('stdout and stderr arguments may not be used '
                             'with capture_output.')
        kwargs['stdout'] = PIPE
        kwargs['stderr'] = PIPE

    def _maybe_text(data):
        if text and data is not None:
            return io.TextIOWrapper(
                io.BytesIO(data),
                encoding=encoding, errors=errors).read()
        return data

    if shell:
        proc = await asyncio.create_subprocess_shell(args, **kwargs)
    else:
        proc = await asyncio.create_subprocess_exec(*args, **kwargs)

    coro = asyncio.create_task(proc.communicate(input))
    try:
        stdout, stderr = await asyncio.wait_for(asyncio.shield(coro), timeout)
    except asyncio.TimeoutError:
        proc.kill()
        stdout, stderr = await coro
        raise TimeoutExpired(
            args, timeout, _maybe_text(stdout), _maybe_text(stderr))
    except asyncio.CancelledError:
        proc.kill()
        raise

    if check and proc.returncode != 0:
        raise CalledProcessError(
            proc.returncode, args,
            _maybe_text(stdout), _maybe_text(stderr))

    return CompletedProcess(
        args, proc.returncode, _maybe_text(stdout), _maybe_text(stderr))
