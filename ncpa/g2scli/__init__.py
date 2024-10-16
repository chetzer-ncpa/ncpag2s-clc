from ncpa.g2scli.settings import config as cli_config
from ncpa.g2scli.commands import ModularCommand
from ncpa.g2scli.version import get_version
from ncpa.g2scli.urls import format_url
from ncpa.g2scli.requests import request_and_write

from ncpa.g2s import G2SProfileSet
from ncpa.g2s.formatters import G2SProfileDecoder, G2SFormatterFactory

import sys
import os
# from configparser import ConfigParser
from datetime import datetime, timezone, timedelta
from io import StringIO
import json

VERSION = (0, 2, 0, "beta", 0)
APPS = ('g2scli')


def execute_from_command_line(argv=None):
    """Run a ModularCommand."""
    utility = ModularCommand(argv)
    utility.execute()

class G2SClient:
    def __init__(self,
                 chunksize=cli_config['requests'].getint('chunksize',2048),
                 encoding=cli_config['requests'].get('encoding','utf-8'),
                 timeout=cli_config['requests'].getint('timeout',30),
                 ):
        self._chunksize = chunksize
        self._encoding = encoding
        self._timeout = timeout
        
    def _fetch_json(self,request_type,**kwargs):
        url = format_url(request_type,
                         outputformat='json',
                         **kwargs)
        holder = StringIO(initial_value='')
        request_and_write(url, 
                          out=holder, 
                          timeout=self._timeout, 
                          chunksize=self._chunksize, 
                          encoding=self._encoding)
        output = json.loads(holder.getvalue(),cls=G2SProfileDecoder)
        holder.close()
        return output
        
        
    def point(self,time,latitude,longitude):
        return self._fetch_json(request_type='point',time=time,latitude=latitude,longitude=longitude)
        
            
        # url = format_url('point', 
        #                  time=time, 
        #                  latitude=latitude, 
        #                  longitude=longitude,
        #                  outputformat='json')
        #
        # holder = StringIO(initial_value='')
        # request_and_write(url, 
        #                   out=holder, 
        #                   timeout=self._timeout, 
        #                   chunksize=self._chunksize, 
        #                   encoding=self._encoding)
        # profile = json.loads(holder.getvalue(),cls=G2SProfileDecoder)
        # holder.close()
        # return profile
    
    def line(self,time,start,end,points):
        return self._fetch_json(request_type='line',
                                time=time,
                                startlatitude=start[0],
                                startlongitude=start[1],
                                endlatitude=end[0],
                                endlongitude=end[1],
                                points=points
                                )
        
    def grid(self,time,start,end,latpoints,lonpoints):
        return self._fetch_json(request_type='grid',
                                time=time,
                                startlatitude=start[0],
                                startlongitude=start[1],
                                endlatitude=end[0],
                                endlongitude=end[1],
                                latpoints=latpoints,
                                lonpoints=lonpoints
                                )
        
    
        
        
        