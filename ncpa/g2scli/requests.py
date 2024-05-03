from urllib import request
from ncpa.g2scli.urls import format_url
from urllib.error import HTTPError

def request_and_write(url, out, timeout, chunksize, encoding):
    with request.urlopen(url, timeout=timeout ) as response:
        nchunks = 0
        while chunk := response.read(chunksize):
            out.write(chunk.decode(encoding))
            nchunks += 1

def time_is_in_database(dt, timeout=None, **kwargs):
    url = format_url('timecheck',time=dt,**kwargs)
    try:
        with request.urlopen(url, timeout=timeout) as _:
            return True
    except HTTPError:
        return False