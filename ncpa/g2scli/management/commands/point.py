from ncpa.g2scli.commands import BaseCommand, docstring_parameter
from ncpa.g2scli.settings import config
from ncpa.g2scli.urls import format_url
from ncpa.g2scli.version import get_parent_name
from ncpa.g2s import G2SProfileSet
from ncpa.g2s.formatters import G2SProfileDecoder, G2SFormatterFactory

from urllib.error import HTTPError
import re
import json
import copy
from io import StringIO

from ncpa.g2scli.options import add_date_arguments, parse_datetimes, add_point_location_arguments
from ncpa.g2scli.commands import CommandError
from ncpa.g2scli.requests import request_and_write

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
        --outputformat ncpaprop --output rasputin.dat
        '''
    ]
    
    def add_arguments(self,parser):
        add_date_arguments(parser,single=True,multiple=True)
        add_point_location_arguments(parser,required=True)
        parser.add_argument(
            "--output", nargs='?', type=str, default=None, help='Output file or directory, as appropriate'
        )
        parser.add_argument(
            "--outputformat", nargs='?', choices=['ncpaprop','json'], default='json', help='Output format'
        )
        # parser.add_argument(
        #     "--pretty", action='store_true', help='After retrieval, reload and reprint in pretty format (JSON only)'
        # )
        
    def handle(self,*args,**options):
        chunksize = config['requests'].getint('chunksize',2048)
        encoding = config['requests'].get('encoding','utf-8')
        timeout = config['requests'].getint('timeout',30)
        
        times = parse_datetimes(options)
        
        tmpformat = 'json'
        finalformat = options['outputformat']
        params = copy.deepcopy(options)
        params['outputformat'] = tmpformat
        
        profiles = G2SProfileSet()
        for t in times:
            url = format_url('point', time=t, **params)
            holder = StringIO()
            try:
                request_and_write(url, 
                                  out=holder, 
                                  timeout=timeout, 
                                  chunksize=chunksize, 
                                  encoding=encoding)
            except HTTPError as err:
                raise CommandError(f'Server returned error {err.code}: {err.reason}')
            profiles.append(json.loads(holder.getvalue(),cls=G2SProfileDecoder))
        
        formatargs={}
        if options['output']:
            formatargs['output'] = options['output']
        if len(profiles) == 1:
            profiles = profiles[0]
        G2SFormatterFactory.factory.create(finalformat).format(profiles,**formatargs)