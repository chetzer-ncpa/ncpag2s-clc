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

ZIP_RE = re.compile('.*filename="?(.+\.zip)')
BIN_RE = re.compile('.*filename="?(.+\.bin)')

@docstring_parameter(get_parent_name())
class Command(BaseCommand):
    '''Request and return a raw data file in .bin format from the G2S server.'''
    
    # help = __doc__
    examples = [
        '%(prog)s --year 2023 --month 7 --day 4 --hour 12',
        
        '''%(prog)s --year 2023 --month 7 --day 4 --hour 12 --outputfile tester.bin --verbosity debug
        '''
    ]
    

    
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
            "--outputfile", nargs='?', type=str, help='Output filename (default is set by server)'
        )
        
    def handle(self,*args,**options):
        logger = self.setup_logging(loggername=__name__,*args,**options)
        
        url = format_url('raw',**options)
        logger.info(f'Built URL={url}')
        
        with request.urlopen(url, timeout=config['requests'].getint('timeout') ) as response:
            outfile = options.get('outputfile')
            if not outfile:
                logging.debug('No output filename, asking server for one')
                m = BIN_RE.search(response.getheader('Content-Disposition'))
                if m:
                    outfile = m.group(1)
                    logger.debug(f'Got filename {outfile} from server')
                else:
                    logger.error('No filename specified and server did not supply one!')
                    raise ValueError('No filename specified and server did not supply one!')
            count = 0
            with open(outfile,'wb') as outfid:
                while chunk := response.read(config['requests'].getint('chunksize')):
                    outfid.write(chunk)
                    count += 1
                logging.debug(f"Read {count} chunks of {config['requests'].getint('chunksize')} bytes")
                
                
                
                
