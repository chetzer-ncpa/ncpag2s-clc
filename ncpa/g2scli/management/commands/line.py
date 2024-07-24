import re
import json
import copy
from io import StringIO
from urllib.error import HTTPError

from ncpa.g2s.formatters import G2SProfileDecoder, G2SFormatterFactory

from ncpa.g2scli.commands import BaseCommand, CommandError
from ncpa.g2scli.settings import config
from ncpa.g2scli.urls import format_url
from ncpa.g2scli.options import add_date_arguments, parse_datetimes, add_line_location_arguments
from ncpa.g2scli.requests import request_and_write

ZIP_RE = re.compile('.*filename="?(.+\.zip)')

class Command(BaseCommand):
    '''Request and return a line of points from the G2S archive.
    
    The user specifies a date and time, starting and ending points, and the number of points
    to return.  If the default JSON format is requested, the results are returned in text 
    format.  If ncpaprop format is requested, a summary file and set of profile files
    are created in the output directory, suitable for use in NCPAprop.
    '''
    
    #help = "Extract a line of points from the G2S database."
    examples = [
        '''
        ncpag2s.py line --date 2023-08-10 --hour 0 --startlat 34.39 --startlon -89.51 
        --endlat 35.23 --endlon -106.66 --points 21
        ''',
        '''
        ncpag2s.py line --date 2023-08-10 --hour 0 --startlat 34.39 --startlon -89.51 
        --endlat 35.23 --endlon -106.66 --points 21 --outputformat ncpaprop 
        --output /tmp/ms_to_abq
        '''
        
    ]
    
    def add_arguments(self,parser):
        add_date_arguments(parser,single=True,multiple=True)
        add_line_location_arguments(parser,required=True)
        parser.add_argument(
            "--output", nargs='?', type=str, default=None, help='Output file or directory, as appropriate'
        )
        parser.add_argument(
            "--outputformat", nargs='?', choices=['ncpaprop','json'], default='json', help='Output format'
        )
        
        
    def handle(self,*args,**options):
        chunksize = config['requests'].getint('chunksize',2048)
        encoding = config['requests'].get('encoding','utf-8')
        timeout = config['requests'].getint('timeout',30)
        
        times = parse_datetimes(options)
        
        tmpformat = 'json'
        finalformat = options['outputformat']
        params = copy.deepcopy(options)
        params['outputformat'] = tmpformat
        
        linelist = []
        for t in times:
            url = format_url('line', time=t, **params)
            holder = StringIO(initial_value='')
            try:
                request_and_write(url, 
                                  out=holder, 
                                  timeout=timeout, 
                                  chunksize=chunksize, 
                                  encoding=encoding)
            except HTTPError as err:
                raise CommandError(f'Server returned error {err.code}: {err.reason}')
            jsontext = holder.getvalue()
            line = json.loads(jsontext,cls=G2SProfileDecoder)
            linelist.append(line)
            holder.close()
        
        formatargs={}
        if options['output']:
            formatargs['output'] = options['output']
        G2SFormatterFactory.factory.create(finalformat).format(
            linelist[0] if len(linelist) == 1 else linelist,
            **formatargs)
        
       