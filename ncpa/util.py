"""
Utility functions and classes

Functions:
break_into_lines(text,length)
    Break a long segment of text on word boundaries (whitespace) into 
    lines of a maximum length
cart2pol(x,y)
    Convert Cartesian coordinates to polar coordinates
get_api_key(apiname,keyfile)
    From a two-column key-value text file, retrieve the value of a key
is_even(i)
    Is the number even?
is_odd(i)
    Is the number odd?
nchoosek(n,k)
    Binomial coefficient or all combinations
nextpow2(x)
    The next highest integer that is an integer power of 2
pol2cart(rho,phi)
    Convert polar coordinates to Cartesian coordinates
qdp(y,x,block)
    Quick-and-dirty single-line plot
test_blank(v,y,n)
    Tests a variable to see if it is blank text, returning options provided
test_null(v,y,n)
    Tests a variable to see if it is None, or a database null
test_null_or_blank(v,y,n)
    Tests both possibilities, returning options provided
to_datetime(v)
    Converts value to datetime object.  Tests a variety of input types

    
Classes:
JulianDate
    Converts date/datetime objects to a Julian date (YYYYDDD) 
Location
    Simple lat/lon/elev location triplet
Messager
    Simple logging to the terminal based on verbosity levels
SpatialAverage
    Spatial averaging functionality
SpatialAverageFactory
    Builder class for SpatialAverage
TimeSeriesGrid
    Convenience class for multiple spatially-related time series
UnpackerFactory
    Creates a Struct unpacker based on endianness, data type, and number
    of samples
"""
from typing import Union

from ncpa.text import remove_dashes


# Simple API key database
def get_api_key(apiname: str, keyfile="~/.api_db") -> str:
    """
    Queries a simple two-column database file.  If the key is found in the first 
    column, it returns the second column value.
    
    :param apiname: The key to be found in the first column
    :type apiname: str
    :param keyfile: The file to be searched, defaults to "~/.api_db"
    :type keyfile: str, optional
    :return: The value associated with apiname, or None      
    :rtype: str
    """
    with open(keyfile) as f:
        db = dict(x.rstrip().split(None,1) for x in f)
    try:
        return db[apiname]
    except LookupError:
        return None





# def jdate(d:Union[datetime.datetime,datetime.date,int,float]) -> int:
#     """
#     Returns the Julian date of a datetime or date object as an integer.
#
#     :param d: The date to convert
#     :type d: date or datetime
#     :return: The Julian date as a 7-digit number
#     :rtype: int
#     """ 
#     if d is None:
#         return None
#     try:
#         return int(d.strftime("%Y%j"))
#     except AttributeError:
#         return datetime.datetime.fromtimestamp(d,tz=datetime.timezone.utc).strftime("%Y%j")

# class Location():
#     def __init__(self,
#                  latitude:Union[float,int],
#                  longitude:Union[float,int],
#                  elevation:Union[float,int]):
#         import numpy as np
#         if np.fabs(latitude) <= 90.0:
#             self.latitude = latitude
#         else:
#             raise ValueError(f"Latitude {latitude} out of range, must be in [-90,90]")
#         self.longitude = longitude
#         self.elevation = elevation
#
#     def normalize(self):
#         while self.longitude <= -180.0:
#             self.longitude += 360.0
#         while self.longitude > 180.0:
#             self.longitude -= 360.0
#


class Messager():
    VERBOSE_SILENT  = 0
    VERBOSE_ERROR   = 1
    VERBOSE_WARNING = 2
    VERBOSE_INFO    = 3
    VERBOSE_DEBUG   = 4
    
    def __init__(self,verbosity=VERBOSE_INFO):
        self._verbosity = verbosity
        
    def set_verbose_level(self,verbosity):
        self._verbosity = verbosity
        
    def set_verbose_level_from_string(self,vstring):
        if vstring.lower().startswith("silent") or vstring.lower().startswith("quiet"):
            self.set_verbose_level(Messager.VERBOSE_SILENT)
        elif vstring.lower().startswith("error"):
            self.set_verbose_level(Messager.VERBOSE_ERROR)
        elif vstring.lower().startswith("warn"):
            self.set_verbose_level(Messager.VERBOSE_WARNING)
        elif vstring.lower().startswith("info"):
            self.set_verbose_level(Messager.VERBOSE_INFO)
        elif vstring.lower().startswith("debug"):
            self.set_verbose_level(Messager.VERBOSE_DEBUG)
        else:
            raise LookupError(f"{vstring} not recognized")
    
    def _message(self,msg,lvl):
        if lvl <= self._verbosity:
            print(msg)
    
    def error(self,msg):
        self._message(msg=msg,lvl=Messager.VERBOSE_ERROR)
        
    def warning(self,msg):
        self._message(msg=msg,lvl=Messager.VERBOSE_WARNING)
        
    def info(self,msg):
        self._message(msg=msg,lvl=Messager.VERBOSE_INFO)
        
    def debug(self,msg):
        self._message(msg=msg,lvl=Messager.VERBOSE_DEBUG)





def parse_args( argv, defaults=None ):
    """
    Returns a dict of arg/value pairs (value is True for flags)
    and a list of bare arguments.
    
    :param argv: The list of arguments
    :type argv: list
    :param defaults: Default argument/value pairs
    :type defaults: dict
    """
    if defaults is None:
        defaults = {}
    pairs = defaults
    bare = []
    args = list(argv)
    while len(args) > 0:
        a = args.pop(0)
        hasdash, stub = remove_dashes(a)
        if hasdash:
            if len(args) > 0:
                nexthasdash, nextstub = remove_dashes(args[0])
                if not nexthasdash:
                    # case 1: flag and argument
                    pairs[stub] = nextstub
                    _ = args.pop(0)
                else:
                    # case 2: flag, and next argument is also flag
                    pairs[stub] = True
            else:
                # case 3: flag and it's the last argument
                pairs[stub] = True
        else:
            # case 4, it's a bare argument, not a flag
            bare.append(stub)
    return pairs, bare
            







        


        

import struct
class UnpackerFactory():
    
    @staticmethod
    def build(byteorder,datatype,n=""):
        boc = UnpackerFactory._get_byte_order_character(byteorder)
        dtc = UnpackerFactory._get_data_type_character(datatype)
        if dtc is None:
            raise RuntimeError(f"Unrecognized data type code {datatype}")
        code = f"{boc}{n}{dtc}"
        return struct.Struct(code)
    
    @staticmethod
    def build_from_css_code(csscode,n=""):
        dtype=csscode[0]
        dsize=csscode[1]
        if dtype.lower() == 't':
            byteorder='big'
            datatype='f'
        elif dtype.lower() == 's':
            byteorder='big'
            datatype='i'
        elif dtype.lower() == 'f':
            byteorder='little'
            datatype='f'
        elif dtype.lower() == 'i':
            byteorder='little'
            datatype='i'
        else:
            raise ValueError("Unrecognized CSS datatype {}".format(csscode))
        dtc = "{}{}".format(datatype,8*int(dsize))
        return UnpackerFactory.build(byteorder=byteorder,datatype=dtc,n=n)
        
    @staticmethod
    def _get_byte_order_character(byteorder):
        if byteorder.lower()[0] == "b":
            return ">"
        elif byteorder.lower()[0] == "l":
            return "<"
        else:
            return "="
    
    @staticmethod
    def _get_data_type_character(datatype):
        if datatype in ["byte","int8","char","i8"]:
            return "b"
        elif datatype in ["ubyte","uint8","uchar","u8"]:
            return "B"
        elif datatype in ["short","short int","int16","i16"]:
            return "h"
        elif datatype in ["unsigned short","unsigned short int","uint16","u16"]:
            return "H"
        elif datatype in ["int","int32","long","long int","i32"]:
            return "i"
        elif datatype in ["uint","uint32","unsigned long","unsigned long int","u32"]:
            return "I"
        elif datatype in ["long long","long long int","int64","i64"]:
            return "q"
        elif datatype in ["unsigned long long","unsigned long long int","uint64","u64"]:
            return "Q"
        elif datatype in ["float","float32","f32"]:
            return "f"
        elif datatype in ["double","float64","f64","d64"]:
            return "d"
        else:
            return None









from datetime import datetime, timezone
import contextlib
import sys

def attrs(obj,attrlist=[],indslist=[],default='__NODEFAULT__'):
    usedefault = (default != '__NODEFAULT__')
    for a in attrlist:
        try:
            return getattr(obj,a)
        except AttributeError:
            pass
    for ind in indslist:
        try:
            return obj[ind]
        except TypeError:
            pass
        except IndexError:
            pass
        except KeyError:
            pass
    if usedefault:
        return default
    else:
        raise ValueError(f'Object has no attributes in [{",".join(attrlist)}] and no indices in [{",".join([str(i) for i in indslist])}]')

def filewritemode(append=False,binary=False):
    return f'{"a" if append else "w"}{"b" if binary else "t"}'

def writer(fn,binary=False,append=False):
    @contextlib.contextmanager
    def stdout():
        yield sys.stdout
    return open(fn,filewritemode(append=append,binary=binary)) if fn else stdout()
