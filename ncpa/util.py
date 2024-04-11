from datetime import datetime, timezone
import contextlib
import sys


def filewritemode(append=False,binary=False):
    return f'{"a" if append else "w"}{"b" if binary else "t"}'

def parseutctime(dtstr):
    return datetime.fromisoformat(dtstr).replace(tzinfo=timezone.utc)

def utcnow():
    return datetime.now(tz=timezone.utc)

def writer(fn,binary=False,append=False):
    @contextlib.contextmanager
    def stdout():
        yield sys.stdout
    return open(fn,filewritemode(append=append,binary=binary)) if fn else stdout()
