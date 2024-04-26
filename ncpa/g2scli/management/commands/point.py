from ncpa.g2scli.commands import BaseCommand, docstring_parameter
from ncpa.g2scli.settings import config
from ncpa.g2scli.urls import format_url
from ncpa.g2scli.version import get_parent_name
from ncpa.util import writer

import logging
from datetime import datetime, timezone
from urllib import request
import re
import json
import sys

from ncpa.g2scli.options import add_date_arguments, parse_datetimes, add_point_location_arguments

ZIP_RE = re.compile('.*filename="?(.+\.zip)')

@docstring_parameter(get_parent_name())
class Command(BaseCommand):
    '''Request a single point from the G2S archive and return it in a text format.
    
    A location and one or more date(s) and time(s) are required.  The resulting 
    profile is returned as plain text in the format specified.
    '''
    
    examples = [
        '%(prog)s --date 2023-07-04 --hour 12 --lat 37.867 --lon -122.259',
        
        '''%(prog)s --date 2023-07-04 --hour 12 --lat 37.867 --lon -122.259
        --outputformat ncpaprop --output rasputin.dat --logfile /tmp/point.log
        --verbosity debug
        '''
    ]
    
    def add_arguments(self,parser):
        add_date_arguments(parser,single=True,requiresingle=True,multiple=False)
        add_point_location_arguments(parser,required=True)
        parser.add_argument(
            "--outputformat", nargs=1, choices=['ncpaprop','json'], default='json', help='Output format'
        )
        parser.add_argument(
            "--pretty", action='store_true', help='After retrieval, reload and reprint in pretty format (JSON only)'
        )
        
    def handle(self,*args,**options):
        logger = self.setup_logging(loggername=__name__,*args,**options)
        
        times = parse_datetimes(options)
        if len(times) > 1:
            raise ValueError(f'{__name__} accepts only one date and time')
        
        url = format_url('point', time=times[0], **options)
        logger.info(f'Built URL={url}')
        
        
        with writer(options.get('output')) as out:
            logger.debug(f'Writing to {options.get("output") if options.get("output") else "stdout"}')
            with request.urlopen(url, timeout=config['requests'].getint('timeout') ) as response:
                logger.debug(f'Received response: status code {response.status}')
                while chunk := response.read(config['requests'].getint('chunksize')):
                    logger.debug(f'Read chunk of {len(chunk)} bytes')
                    out.write(chunk.decode(config['requests'].get('encoding')))
        
        if options.get('pretty') and options.get('outputformat') == 'json' and options.get('output'):
            with open(options.get('output'),'rt') as fid:
                contents = json.load(fid)
            with open(options.get('output'),'wt') as fid:
                fid.write(json.dumps(contents,indent=4))
            
        