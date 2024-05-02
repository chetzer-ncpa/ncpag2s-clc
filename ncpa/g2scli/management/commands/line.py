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
        --output /tmp/ms_to_abq --verbosity debug
        '''
        
    ]
    
    def add_arguments(self,parser):
        # parser.add_argument(
        #     "--year", nargs='?', required=True, type=int, help="Year"
        # )
        # parser.add_argument(
        #     "--month", nargs='?', required=True, type=int, help="Month (1-12)"
        # )
        # parser.add_argument(
        #     "--day", nargs='?', required=True, type=int, help="Day (1-31)"
        # )
        # parser.add_argument(
        #     "--hour", nargs='?', required=True, type=int, help="Hour (0-23)"
        # )
        # parser.add_argument(
        #     "--lat", nargs='?', required=True, type=float, help="Starting point latitude"
        # )
        # parser.add_argument(
        #     "--lon", nargs='?', required=True, type=float, help="Starting point longitude"
        # )
        # parser.add_argument(
        #     "--endlat", nargs='?', required=True, type=float, help="Ending point latitude"
        # )
        # parser.add_argument(
        #     "--endlon", nargs='?', required=True, type=float, help="Ending point longitude"
        # )
        # parser.add_argument(
        #     "--points", nargs='?', required=True, help="Number of points"
        # )
        add_date_arguments(parser,single=True,multiple=True)
        add_line_location_arguments(parser,required=True)
        parser.add_argument(
            "--outputformat", nargs='?', choices=['ncpaprop','json'], default='json', help='Output format'
        )
        # parser.add_argument(
        #     "--pretty", action='store_true', help='After retrieval, reload and reprint in pretty format (JSON only)'
        # )
        
        
    def handle(self,*args,**options):
        logger = self.setup_logging(loggername=__name__,*args,**options)
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
            logger.debug(f'Built URL={url}')
            # print(url)
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
        
        
        
        
        # logger = self.setup_logging(loggername=__name__,*args,**options)
        #
        # times = parse_datetimes(options)
        # if len(times) > 1:
        #     raise ValueError(f'{__name__} accepts only one date and time')
        #
        # url = format_url('line', time=times[0], **options)
        # logger.info(f'Built URL={url}')
        # # url = f'https://g2s.ncpa.olemiss.edu/g2sv2/g2sdb/line/{t0.year}/{t0.month}/{t0.day}/{t0.hour}/{startlat}/{startlon}/{endlat}/{endlon}/{npoints}/'
        #
        # if options.get('outputformat') == 'ncpaprop':
        #     if not options.get('output'):
        #         raise ValueError('NCPAProp format for a line requires a directory to be specified with --output')
        #     with tempfile.NamedTemporaryFile() as out:
        #         logger.debug(f'Opened temporary file: {out.name}')
        #         with request.urlopen(url, timeout=config['requests'].getint('timeout') ) as response:
        #             logger.debug(f'Received response: status code {response.status}')
        #             bytes_out = 0
        #             while chunk := response.read(config['requests'].getint('chunksize')):
        #                 bytes_out += out.write(chunk)
        #             logger.debug(f'Wrote {bytes_out} bytes to file')
        #         out.flush()
        #         with open(out.name,'rt') as tmpin:
        #             logger.debug(f'Reading JSON data from {out.name} to convert')
        #             line = json.load(tmpin,cls=G2SProfileDecoder)
        #     NCPAPropG2SFormatter().format_line(line,output_dir=options.get('output'))
        #     logger.debug(f'Line written to {options.get("output") if options.get("output") else "stdout"}')
        #
        # elif options.get('outputformat') == 'json':
        #
        #     if options.get('pretty'):
        #         with tempfile.NamedTemporaryFile() as out:
        #             logger.debug(f'Writing JSON to temp file {out.name}')
        #             with request.urlopen(url, timeout=config['requests'].getint('timeout') ) as response:
        #                 logger.debug(f'Received response: status code {response.status}')
        #                 bytes_out = 0
        #                 while chunk := response.read(config['requests'].getint('chunksize')):
        #                     bytes_out += out.write(chunk.decode(config['requests'].get('encoding')).encode('utf-8'))
        #                 logger.debug(f'Wrote {bytes_out} bytes to file')
        #             out.flush()
        #             with open(out.name,'rt') as tmpin:
        #                 contents = json.load(tmpin)
        #         with writer(options.get('output')) as fid:
        #             fid.write(json.dumps(contents,indent=4))
        #             fid.write('\n')
        #     else:
        #         with writer(options.get('output')) as out:
        #             logger.debug(f'Writing JSON to {options.get("output") if options.get("output") else "stdout"}')
        #             with request.urlopen(url, timeout=config['requests'].getint('timeout') ) as response:
        #                 logger.debug(f'Received response: status code {response.status}')
        #                 bytes_out = 0
        #                 while chunk := response.read(config['requests'].getint('chunksize')):
        #                     bytes_out += out.write(chunk.decode(config['requests'].get('encoding')))
        #                 logger.debug(f'Wrote {bytes_out} bytes to file')
        #
        # # if options.getboolean('pretty') and options.get('outputformat') == 'json' and options.get('output'):
        # #     with open(options.get('output'),'rt') as fid:
        # #         contents = json.load(fid)
        # #     with open(options.get('output'),'wt') as fid:
        # #         fid.write(json.dumps(contents,indent=4))
        #
        #
        #
