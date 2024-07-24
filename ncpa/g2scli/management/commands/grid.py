import re
import json
import copy
from io import StringIO
from urllib.error import HTTPError

from ncpa.g2s.formatters import G2SProfileDecoder, G2SFormatterFactory

from ncpa.g2scli.commands import BaseCommand, CommandError
from ncpa.g2scli.settings import config
from ncpa.g2scli.urls import format_url
from ncpa.g2scli.options import add_date_arguments, parse_datetimes, add_grid_location_arguments
from ncpa.g2scli.requests import request_and_write

ZIP_RE = re.compile('.*filename="?(.+\.zip)')

class Command(BaseCommand):
    '''Request and return a grid of points from the G2S archive.
    
    The user specifies a date and time, corner points points, and the number of grid points
    to return.  If the default JSON format is requested, the results are returned in text 
    format.  If infraga format is requested, summary files and profile files
    are created in the output directory, suitable for use in infraga-rngdep.
    In addition, a 'flags.txt' file will be created in the execution directory with
    the appropriate flags to feed the grid into InfraGA.
    '''
    
    #help = "Extract a line of points from the G2S database."
    examples = [
        '''
        ncpag2s.py grid --date 2023-08-10 --hour 0 --startlat 34.0 --startlon -89.0 
        --endlat 40.0 --endlon -96.0 --latpoints 13 --lonpoints 15
        ''',
        '''
        ncpag2s.py grid --date 2023-08-10 --hour 0 --startlat 34.39 --startlon -89.51 
        --endlat 35.23 --endlon -106.66 --points 21 --outputformat infraga 
        --output /tmp/testgrid
        '''
    ]
    
    def add_arguments(self,parser):
        add_date_arguments(parser,single=True,multiple=False)
        add_grid_location_arguments(parser,required=True)
        parser.add_argument(
            "--outputformat", nargs='?', choices=['json','infraga'], default='json', help='Output format'
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
        
        t = times[0]
        
        url = format_url('grid', time=t, **params)
        holder = StringIO(initial_value='')
        try:
            request_and_write(
                url, 
                out=holder, 
                timeout=timeout, 
                chunksize=chunksize, 
                encoding=encoding)
        except HTTPError as err:
            raise CommandError(f'Server returned error {err.code}: {err.reason}')
        jsontext = holder.getvalue()
        grid = json.loads(jsontext,cls=G2SProfileDecoder)
        holder.close()
        grid.sort()
        
        formatargs={}
        if options['output']:
            formatargs['output'] = options['output']
        G2SFormatterFactory.factory.create(finalformat).format(grid,**formatargs)
