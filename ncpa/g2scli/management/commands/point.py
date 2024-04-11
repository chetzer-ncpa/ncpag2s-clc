from ncpa.g2scli.commands import BaseCommand
from ncpa.g2scli.settings import config
from ncpa.g2scli.urls import format_url
from ncpa.util import writer

import logging
from datetime import datetime, timezone
from urllib import request
import re

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
    help = "Extract a single point from the G2S archive"
    
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
            "--lat", nargs='?', required=True, help="Location for profile"
        )
        parser.add_argument(
            "--lon", nargs='?', required=True, type=float, help="Location for profile"
        )
        parser.add_argument(
            "--outputformat", nargs='?', choices=['ncpaprop','json'], default='json', help='Output format'
        )
        parser.add_argument(
            "--output", nargs='?', default=None, help='Output file (stdout or point_request.zip depending on response type)'
        )
        
    def handle(self,*args,**options):
        
        # starttime = options.get("time")
        # latitude = options.get("latitude")
        # longitude = options.get("longitude")
        # output_format = options.get("format")
        # output = options.get("output")
        #
        # try:
        #     t0 = datetime.fromisoformat(starttime).replace(tzinfo=timezone.utc)
        #     logging.debug(f'Parsed start time as {t0}')
        # except ValueError:
        #     logging.error(f'Start date/time {starttime} not in parseable format')
        #     exit(1)
        #
        # url = 'https://g2s.ncpa.olemiss.edu/g2sv2/g2sdb/extract/{year}/{month}/{day}/{hour}/{lat}/{lon}/{form}/'.format(
        #     year=t0.year,
        #     month=t0.month,
        #     day=t0.day,
        #     hour=t0.hour,
        #     lat=latitude,
        #     lon=longitude,
        #     form=output_format,
        # )
        # with writer(output) as out:
        #     with request.urlopen(url, timeout=30 ) as response:
        #         out.write(response.read().decode('utf-8'))
        logger = self.setup_logging(loggername=__name__,*args,**options)
        url = format_url('point',**options)
        logger.info(f'Built URL={url}')
        with writer(options.get('output')) as out:
            logger.debug(f'Writing JSON to {options.get("output") if options.get("output") else "stdout"}')
            with request.urlopen(url, timeout=config['requests'].getint('timeout') ) as response:
                logger.debug(f'Received response: status code {response.status}')
                while chunk := response.read(config['requests'].getint('chunksize')):
                    logger.debug(f'Read chunk of {len(chunk)} bytes')
                    out.write(chunk.decode(config['requests'].get('encoding')))
        
        # with writer(options.get('output')) as out:
        #     with request.urlopen(url, timeout=30) as response:
        #         while chunk := response.read(200):
        #             out.write(chunk.decode('utf-8'))
            
        