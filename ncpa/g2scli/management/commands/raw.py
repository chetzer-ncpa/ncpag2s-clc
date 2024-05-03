from ncpa.g2scli.commands import BaseCommand, docstring_parameter, CommandError
from ncpa.g2scli.settings import config
from ncpa.g2scli.urls import format_url
from ncpa.g2scli.version import get_parent_name
from ncpa.g2scli.options import add_date_arguments, parse_datetimes

import logging
from urllib import request
from urllib.error import HTTPError
import re

ZIP_RE = re.compile('.*filename="?(.+\.zip)')
BIN_RE = re.compile('.*filename="?(.+\.bin)')

@docstring_parameter(get_parent_name())
class Command(BaseCommand):
    '''Request and return a raw data file in .bin format from the G2S server.'''
    
    # help = __doc__
    examples = [
        '%(prog)s --date 2023-07-04 --hour 12',
        
        '''%(prog)s --date 2023-07-04 --hour 12 --outputfile tester.bin --verbosity debug
        '''
    ]
    

    
    def add_arguments(self,parser):
        add_date_arguments(parser,single=True,multiple=False,requiresingle=True)
        parser.add_argument(
            "--outputfile", nargs='?', type=str, help='Output filename (default is set by server)'
        )
        
    def handle(self,*args,**options):
        logger = self.setup_logging(loggername=__name__,*args,**options)
        
        times = parse_datetimes(options)
        
        url = format_url('raw',time=times[0],**options)
        logger.info(f'Built URL={url}')
        
        try:
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
        except HTTPError as err:
            raise CommandError(f'Server returned error {err.code}: {err.reason}')
                
                
                
