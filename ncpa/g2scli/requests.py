from urllib import request


def request_and_write(url, out, timeout, chunksize, encoding):
    with request.urlopen(url, timeout=timeout ) as response:
        nchunks = 0
        while chunk := response.read(chunksize):
            out.write(chunk.decode(encoding))
            nchunks += 1
    