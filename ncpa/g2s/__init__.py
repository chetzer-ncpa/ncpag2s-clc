import re
from datetime import datetime, timezone
import json
import os
import logging

from ncpa.geographic import Location, GeographicDistance
import ncpa.object_factory as object_factory
from ncpa.mixins import Dictable, HasMetadata

# from .formatters import G2SFormatterFactory, G2SProfileSetJSONIterator
from .exceptions import BadProfileError

G2S_DEFAULT_DZ = 0.1
G2S_DEFAULT_ZMAX = 150.0


class G2SFile:
    def __init__(self,filename,time=None):
        self.filename = filename
        (self.source_code, fnt) = self.parse_filename(filename)
        if time is None:
            self.time = fnt
        else:
            self.time = time
            
    def parse_filename(self,filename=None):
        if filename is None:
            filename = self.filename
        m = re.match(r'.*G2SGCS(?P<source_code>.)(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})(?P<hour>\d{2})\.bin$',filename)
        if m:
            return (
                m.group('source_code'),
                datetime(int(m.group('year')),int(m.group('month')),int(m.group('day')),hour=int(m.group('hour')),tzinfo=timezone.utc),
                )

class G2SParameter(Dictable):
    def __init__(self,code=None,description=None,units=None,values=[]):
        self.code = code.upper()
        self.description = description
        self.units = units
        self.values = values
        
    def as_dict(self):
        return {
            'parameter': self.code,
            'description': self.description,
            'units': self.units,
            'n': len(self.values),
            'values': self.values,
        }
        
    def scale(self,factor):
        self.values = [v*factor for v in self.values]
    
    def offset(self,factor):
        self.values = [v+factor for v in self.values]

        
class G2SProfile(HasMetadata):
    time_format_string = '%Y-%m-%dT%H:%M:%SZ'
    
    def __init__(self,sourcefile=None,nz=0,dz=None,latitude=None,longitude=None,
                 location=None, time=None, tag=None, parameters=[], from_json=None):
        super().__init__(self)
        self.set_metadata('sourcefile',os.path.split(sourcefile)[-1] if sourcefile else None)
        self.set_metadata('tag',tag)
        self.set_metadata('nz',nz)
        self.set_metadata('time',time)
        self.set_metadata('location',location if location else Location(latitude,longitude))
        self.set_metadata('parameters',0)
        
        self.parameters = {}
        for p in parameters:
            self.add_parameter( p )
        if from_json is not None:
            self.import_from_json(from_json)

    def add_parameter(self,p):
        new_nz = len(p.values)
        if new_nz > 1:
            if not self.get_metadata('nz'):
                self.set_metadata('nz',len(p.values))
            elif self.get_metadata('nz') != new_nz:
                raise ValueError(f'Mismatch in number of points: output structure has {self.nz} but new parameter has {new_nz}')
        self.parameters[p.code.upper()] = p
        self.update_metadata()
        
    def update_metadata(self):
        self.set_metadata('parameters',len(self.parameters))
        
    def get_data_vectors(self,codes):
        vectors = []
        for c in codes:
            vectors.append( self.parameters[c].values )
        return vectors
    
    def as_dict(self,*args,**kwargs):
        self.update_metadata()
        return {
            'metadata': self.metadata,
            'data': [
                {
                    'parameter': self.parameters[p].code,
                    'description': self.parameters[p].description,
                    'units': self.parameters[p].units,
                    'n': len(self.parameters[p].values),
                    'values': self.parameters[p].values,
                } for p in self.parameters
            ],
        }
        
    def import_from_json(self,json_in):
        jsdict = json.loads(json_in)
        self.clear_metadata()
        for k in jsdict['metadata']:
            self.set_metadata(k,jsdict['metadata'][k])
        for param in jsdict['data']:
            self.parameters.append( G2SParameter(code=param['parameter'],
                             description=param['description'],
                             units=param['units'],
                             values=[float(val) for val in param['values']],
                             ) )
        self.update_metadata()
            
    def json(self,indent=None):
        return json.dumps(self.as_dict(),indent=indent)
        
    def timestr(self,t):
        return t.strftime(self.time_format_string)
    
    @property
    def location(self):
        return self.get_metadata('location')
    
    @property
    def time(self):
        return self.get_metadata('time')

    
class G2SProfileSet(HasMetadata):
    def __init__(self,set_type='points',profiles=[],locations=[],*args,**kwargs):
        super().__init__(self)
        self.set_metadata('type', set_type)
        self.set_metadata('points',0)
        self.profiles = profiles
        self.locations = locations
        
    def clear(self):
        self.profiles = []
        self.update_metadata()
    
    def extend(self, other):
        self.profiles.extend(other.profiles)
        self.update_metadata()
        
    def append(self,profile):
        self.profiles.append(profile)
        self.update_metadata()
        
    def add_location(self,loc):
        self.locations.append(loc)
        
    def update_metadata(self):
        if self.profiles:
            self.set_metadata('points', len(self.profiles))
        elif self.locations:
            self.set_metadata('points', len(self.locations))
        else:
            self.set_metadata('points', 0)
    
    def __len__(self):
        return len(self.profiles)
    
    def __getitem__(self,index):
        return self.profiles[index]
    
    def as_dict(self,*args,**kwargs):
        self.finalize()
        return {
            'metadata': self.metadata,
            'points': [p.as_dict(*args,**kwargs) for p in self.profiles],
        }
        
    def get_profiles(self):
        return self.profiles
    
    def finalize(self):
        self.update_metadata()
        
    def read(self,reader,*args,**kwargs):
        for loc in self.locations:
            self.append(reader.read_profile(location=loc,*args,**kwargs))
        self.update_metadata()
        
    def modify_profile(self,profile):
        return profile
        
    def stream(self,reader,*args,**kwargs):
        self.update_metadata()
        return (self.modify_profile(reader.read_profile(location=loc,*args,**kwargs)) for loc in self.locations)
            
    @property
    def points(self):
        return len(self.profiles)
            
class G2SProfileLine(G2SProfileSet):
    def __init__(self,reference_location=None,*args,**kwargs):
        super().__init__(set_type='line',*args,**kwargs)
        self.clear()
        self.reference_location = reference_location
        
    def clear(self):
        self.reference_location = None
        super().clear()
        
    def range_to(self,profile=None,lat=None,lon=None):
        try:
            rlat = self.reference_location.latitude
            rlon = self.reference_location.longitude
        except AttributeError:
            raise BadProfileError(f'Reference profile invalid or not set: no latitude or longitude field')
        if profile:
            try:
                plat = profile.location.latitude
                plon = profile.location.longitude
            except AttributeError:
                raise BadProfileError(f'Distal profile invalid or not set: no latitude or longitude field')
        else:
            plat = lat
            plon = lon
        return round(GeographicDistance(rlat,rlon,plat,plon),3)
    
    def finalize(self):
        self.update_metadata()
        self.sort_by_range()
    
    def update_metadata(self):
        super().update_metadata()
        if not self.reference_location:
            if self.profiles:
                self.reference_location = self.profiles[0].get_metadata('location')
            elif self.locations:
                self.reference_location = self.locations[0]
            else:
                self.reference_location = None
        self.set_metadata('reference_location', self.reference_location)
    
    def sort_by_range(self):
        if self.profiles:
            for p in self.profiles:
                p.set_metadata('range', self.range_to(lat=p.location.latitude,
                                                      lon=p.location.longitude))
            self.profiles.sort(key=lambda p: p.metadata['range'])
        if self.locations:
            self.locations.sort(key=lambda p: self.range_to(lat=p.latitude,
                                                            lon=p.longitude))
                
            
    def as_dict(self,*args,**kwargs):
        self.finalize()
        return super().as_dict()
    
    def modify_profile(self,profile):
        profile.set_metadata('range',self.range_to(lat=profile.get_metadata('location').latitude,
                                                   lon=profile.get_metadata('location').longitude))
        return profile
        
    
class G2SProfileGrid(G2SProfileSet):
    _default_sort_ = ('y','x')
    
    def __init__(self,*args,**kwargs):
        super().__init__(set_type='grid',*args,**kwargs)
        
    def finalize(self):
        self.update_metadata()
        self.assign_grid_indices()
        # self.sort_by_xy()
        
    def as_dict(self,*args,**kwargs):
        self.finalize()
        return super().as_dict()
        # return self.assign_grid_indices(super().as_dict(*args,**kwargs))
        
    def get_unique_coordinates(self):
        lats = set()
        lons = set()
        for p in self.profiles:
            lats.add(p.location.latitude)
            lons.add(p.location.longitude)
        return list(sorted(lats)), list(sorted(lons))
    
    def assign_grid_indices(self,sort=True):
        lats, lons = self.get_unique_coordinates()
        lat_dict = {lat: i for (i,lat) in enumerate(sorted(lats))}
        lon_dict = {lon: i for (i,lon) in enumerate(sorted(lons))}
        for p in self.profiles:
            p.set_metadata('x_index',lon_dict[p.location.longitude])
            p.set_metadata('y_index',lat_dict[p.location.latitude])
        if sort:
            self.sort(firstindex='y')
        
    def sort(self,firstindex='y'):
        if firstindex.lower() != 'y' and firstindex.lower() != 'x':
            raise ValueError(f'First index provided is {firstindex}, must be "x" or "y"')
        if firstindex == 'y':
            self.profiles.sort(key=lambda p: (p.metadata['y_index'],p.metadata['x_index']))
        else:
            self.profiles.sort(key=lambda p: (p.metadata['x_index'],p.metadata['y_index']))
        
                
    
    # def sort_by_xy(self):
    #     lats, lons = self.get_unique_coordinates()
    #     latdict = {k: i for (i,k) in enumerate(sorted(lats))}
    #     londict = {k: i for (i,k) in enumerate(sorted(lons))}
    #     self.profiles.sort(key=lambda p: (londict[p.location.longitude],latdict[p.location.latitude]))
        
    
# factories
# class G2SProfileSetBuilder:
#     def __init__(self):
#         self._instance = None
#
#     def __call__(self):
#         return G2SProfileSet()
#         # if not self._instance:
#         #     # self._instance = None
#         #     self._instance = G2SProfileSet()
#         # return self._instance
#
# class G2SProfileLineBuilder:
#     def __init__(self):
#         self._instance = None
#
#     def __call__(self):
#         return G2SProfileLine()
#         # if not self._instance:
#         #     # self._instance = None
#         #     self._instance = G2SProfileLine()
#         # return self._instance
#
# class G2SProfileGridBuilder:
#     def __init__(self):
#         self._instance = None
#
#     def __call__(self):
#         return G2SProfileGrid()
#         # if not self._instance:
#         #     # self._instance = None
#         #     self._instance = G2SProfileGrid()
#         # return self._instance

def _create_g2s_profile_set(**kwargs):
    return G2SProfileSet(**kwargs)
def _create_g2s_profile_line(**kwargs):
    return G2SProfileLine(**kwargs)
def _create_g2s_profile_grid(**kwargs):
    return G2SProfileGrid(**kwargs)
    
# invoke with G2SProfileSetFactory.factory.create('ncpaprop')
class G2SProfileSetFactory:
    factory = object_factory.ObjectFactory()
    factory.register_builder('points',_create_g2s_profile_set)
    factory.register_builder('line',_create_g2s_profile_line)
    factory.register_builder('grid',_create_g2s_profile_grid)



class G2SReader:
    def __init__(self, nrlg2s, sigfigs=6, dz=G2S_DEFAULT_DZ, zmax=G2S_DEFAULT_ZMAX):
        self.nrlg2s_ = nrlg2s
        self.loaded_ = None
        self.sigfigs = sigfigs
        self.dz = dz
        self.zmax = zmax
        
    def load(self,file):
        if self.nrlg2s_.serverup:
            if self.loaded_ and self.loaded_.filename == file.filename:
                return
        
        # make sure file exists and is readable.  Allow IOErrors to propagate
        with open(file.filename,'rb') as testfid:
            _ = testfid.read(1)
            
        self.nrlg2s_.load(file.filename)
        if self.nrlg2s_.serverup:
            self.loaded_ = file
        else:
            raise RuntimeError(f'G2S couldn''t load {file.filename}!')
        
    def extract_profile_set(self,set_type='points',locations=[],*args,**kwargs):
        profiles = G2SProfileSetFactory.factory.create(set_type)
        for loc in locations:
            profiles.append(self.read_profile(lat=loc.latitude,lon=loc.longitude,*args,**kwargs))
        return profiles
    
    def read_profile(self,location=None,lat=None,lon=None,dz=None,zmax=None,*args,**kwargs):
        if dz is None:
            dz = self.dz
        if zmax is None:
            zmax = self.zmax
        if location is None:
            loc = Location(lat,lon)
        else:
            loc = location
        try:
            tag = loc.name
        except AttributeError:
            tag = None
        nz = int(zmax/dz) + 1
        (z0, z, t, u, v, r, p) = self.read_from_nrlg2s(loc.lat,loc.lon,dz,nz)
        profile = G2SProfile(
            sourcefile=self.loaded_.filename,
            nz=nz,
            dz=dz,
            location=loc,
            time=self.loaded_.time,
            tag=tag,
        )
        profile.add_parameter(G2SParameter(code='Z0',description='Ground Height',units='km',values=[z0]))
        profile.add_parameter(G2SParameter(code='Z',description='Height',units='km',values=z))
        profile.add_parameter(G2SParameter(code='T',description='Temperature',units='K',values=t))
        profile.add_parameter(G2SParameter(code='U',description='Zonal Winds',units='m/s',values=u))
        profile.add_parameter(G2SParameter(code='V',description='Meridional Winds',units='m/s',values=v))
        profile.add_parameter(G2SParameter(code='R',description='Density',units='g/cm3',values=r))
        profile.add_parameter(G2SParameter(code='P',description='Pressure',units='mbar',values=p))
        return profile
    
    def read_z0(self,lat,lon):
        return self.nrlg2s_.zgrnd(lat,lon)
        
    def read_from_nrlg2s(self,lat,lon,dz,nz):
        if not self.nrlg2s_.serverup:
            raise RuntimeError(f'G2S server not loaded')
        z0 = self.round_to_sigfigs( self.read_z0(lat,lon) )
        z, t, u, v, r, p = self.nrlg2s_.extract(lat,lon,dz,nz)
        z = list(self.round_to_sigfigs( z ))
        t = list(self.round_to_sigfigs( t ))
        u = list(self.round_to_sigfigs( u ))
        v = list(self.round_to_sigfigs( v ))
        r = list(self.round_to_sigfigs( r ))
        p = list(self.round_to_sigfigs( p ))
        
        return (z0, z, t, u, v, r, p)
    
    def round_to_sigfigs(self,val):
        if self.sigfigs:
            try:
                newvals = []
                for v in iter(val):
                    newvals.append(float(f'{v:0.{self.sigfigs-1}}'))
                return newvals
            except TypeError:
                return float(f'{val:0.{self.sigfigs-1}}')
        else:
            return val
                
                
                