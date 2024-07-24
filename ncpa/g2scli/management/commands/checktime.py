from ncpa.g2scli.commands import BaseCommand, docstring_parameter, CommandError
from ncpa.g2scli.version import get_parent_name
from ncpa.g2scli.options import add_date_arguments, parse_datetimes
from ncpa.g2scli.requests import time_is_in_database

import re

ZIP_RE = re.compile('.*filename="?(.+\.zip)')
BIN_RE = re.compile('.*filename="?(.+\.bin)')

@docstring_parameter(get_parent_name())
class Command(BaseCommand):
    '''Determine if a time is available to extract'''
    
    # help = __doc__
    examples = [
        '%(prog)s --date 2023-08-01 --hour 12',
    ]
    

    
    def add_arguments(self,parser):
        add_date_arguments(parser,single=True,multiple=False,requiresingle=True)
        
    def handle(self,*args,**options):
        times = parse_datetimes(options)
        if time_is_in_database(times[0], **options):
            print(f"Time {times[0].strftime('%Y-%m-%d %H:00:00')} UTC is available")
        else:
            print(f"Time {times[0].strftime('%Y-%m-%d %H:00:00')} UTC is not available")
            
                
                
