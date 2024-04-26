from datetime import datetime, timezone
import contextlib
import sys

def attrs(obj,attrlist=[],indslist=[],default='__NODEFAULT__'):
    usedefault = (default != '__NODEFAULT__')
    for a in attrlist:
        try:
            return getattr(obj,a)
        except AttributeError:
            pass
    for ind in indslist:
        try:
            return obj[ind]
        except TypeError:
            pass
        except IndexError:
            pass
        except KeyError:
            pass
    if usedefault:
        return default
    else:
        raise ValueError(f'Object has no attributes in [{",".join(attrlist)}] and no indices in [{",".join([str(i) for i in indslist])}]')

def filewritemode(append=False,binary=False):
    return f'{"a" if append else "w"}{"b" if binary else "t"}'

# def parseutctime(dtstr):
#     return datetime.fromisoformat(dtstr).replace(tzinfo=timezone.utc)
#
# def roundtime(t,nearest):
#     if nearest == 'day':
#         return t.replace(hour=0,minute=0,second=0,microsecond=0)
#     elif nearest == 'hour':
#         return t.replace(minute=0,second=0,microsecond=0)
#     elif nearest == 'minute':
#         return t.replace(second=0,microsecond=0)
#     elif nearest == 'second':
#         return t.replace(microsecond=0)
#
# def utcnow():
#     return datetime.now(tz=timezone.utc)

def writer(fn,binary=False,append=False):
    @contextlib.contextmanager
    def stdout():
        yield sys.stdout
    return open(fn,filewritemode(append=append,binary=binary)) if fn else stdout()
