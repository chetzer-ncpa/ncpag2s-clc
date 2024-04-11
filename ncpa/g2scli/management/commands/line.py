from ncpa.g2scli.commands import BaseCommand
from ncpa.util import writer, parseutctime
from ncpa.g2s.formatters import G2SProfileDecoder, NCPAPropG2SFormatter
import logging
from datetime import datetime, timezone
from urllib import request
import re
import sys
import json
import tempfile

from ncpa.g2scli.settings import config
from ncpa.g2scli.urls import format_url

# patch HTTPResponse
# from http.client import IncompleteRead, HTTPResponse
# def patch_http_response_read(func):
#     def inner(args):
#         try:
#             return func(args)
#         except IncompleteRead as e:
#             return e.partial
#     return inner
# HTTPResponse.read = patch_http_response_read(HTTPResponse.read)

ZIP_RE = re.compile('.*filename="?(.+\.zip)')

class Command(BaseCommand):
    help = "Extract a line of points from the G2S database."
    
    def add_arguments(self,parser):
        parser.add_argument(
            "--year", nargs='?', required=True, type=int, help="Year"
        )
        parser.add_argument(
            "--month", nargs='?', required=True, type=int, help="Month (1-12)"
        )
        parser.add_argument(
            "--day", nargs='?', required=True, type=int, help="Day (1-31)"
        )
        parser.add_argument(
            "--hour", nargs='?', required=True, type=int, help="Hour (0-23)"
        )
        parser.add_argument(
            "--lat", nargs='?', required=True, type=float, help="Starting point latitude"
        )
        parser.add_argument(
            "--lon", nargs='?', required=True, type=float, help="Starting point longitude"
        )
        parser.add_argument(
            "--endlat", nargs='?', required=True, type=float, help="Ending point latitude"
        )
        parser.add_argument(
            "--endlon", nargs='?', required=True, type=float, help="Ending point longitude"
        )
        parser.add_argument(
            "--points", nargs='?', required=True, help="Number of points"
        )
        parser.add_argument(
            "--outputformat", nargs='?', choices=['ncpaprop','json'], default='json', help='Output format'
        )
        parser.add_argument(
            "--output", nargs='?', default=None, help='Output filename (for JSON format) or directory (for NCPAProp format)'
        )
        
        
    def handle(self,*args,**options):
        # starttime = options.get("time")
        # startlat = options.get("lat")
        # startlon = options.get("lon")
        # endlat = options.get("endlat")
        # endlon = options.get("endlon")
        # npoints = options.get("points")
        # output = options.get("output")
        # outputformat = options.get("format")
        
        # try:
        #     t0 = datetime.fromisoformat(starttime).replace(tzinfo=timezone.utc)
        #     logging.debug(f'Parsed start time as {t0}')
        # except ValueError:
        #     logging.error(f'Start date/time {starttime} not in parseable format')
        #     exit(1)
        logger = self.setup_logging(loggername=__name__,*args,**options)
            
        url = format_url('line',**options)
        logger.info(f'Built URL={url}')
        # url = f'https://g2s.ncpa.olemiss.edu/g2sv2/g2sdb/line/{t0.year}/{t0.month}/{t0.day}/{t0.hour}/{startlat}/{startlon}/{endlat}/{endlon}/{npoints}/'
        
        if options.get('outputformat') == 'ncpaprop':
            if not options.get('output'):
                raise ValueError('NCPAProp format for a line requires a directory to be specified with --output')
            with tempfile.NamedTemporaryFile() as out:
                logger.debug(f'Opened temporary file: {out.name}')
                with request.urlopen(url, timeout=config['requests'].getint('timeout') ) as response:
                    logger.debug(f'Received response: status code {response.status}')
                    while chunk := response.read(config['requests'].getint('chunksize')):
                        logger.debug(f'Read chunk of {len(chunk)} bytes')
                        out.write(chunk)
                out.flush()
                with open(out.name,'rt') as tmpin:
                    logger.debug(f'Reading JSON data from {out.name} to convert')
                    line = json.load(tmpin,cls=G2SProfileDecoder)
            NCPAPropG2SFormatter().format_line(line,output_dir=options.get('output'))
            logger.debug(f'Line written to {options.get("output") if options.get("output") else "stdout"}')
        elif options.get('outputformat') == 'json':
            with writer(options.get('output')) as out:
                logger.debug(f'Writing JSON to {options.get("output") if options.get("output") else "stdout"}')
                with request.urlopen(url, timeout=config['requests'].getint('timeout') ) as response:
                    logger.debug(f'Received response: status code {response.status}')
                    while chunk := response.read(config['requests'].getint('chunksize')):
                        # logger.debug(f'Read chunk of {len(chunk)} bytes')
                        out.write(chunk.decode(config['requests'].get('encoding')))
        
            
            
            
            