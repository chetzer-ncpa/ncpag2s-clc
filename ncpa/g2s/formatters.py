from datetime import datetime, timezone
import json
from ncpa.object_factory import ObjectFactory
from ncpa.json import RoundingEncoder, ExtendedDecoder
from ncpa.g2s import G2SProfile, G2SParameter, G2SProfileSetFactory
import os

from ncpa.geographic import Location

NCPA_G2S_DEFAULT_JSON_INDENT = "\t"
NCPA_G2S_DEFAULT_JSON_FLOAT_FORMAT = '0.5e'
NCPA_G2S_DEFAULT_SIGNIFICANT_DIGITS = 6
NCPA_G2S_DEFAULT_JSON_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

class G2SProfileEncoder(RoundingEncoder):
    def __init__(self,timeformat=NCPA_G2S_DEFAULT_JSON_TIME_FORMAT,*args,**kwargs):
        super().__init__(sigfigs=NCPA_G2S_DEFAULT_SIGNIFICANT_DIGITS,*args,**kwargs)
        self.timeformat = timeformat
        
    def encode_datetime(self,obj):
        return {
            'datetime': obj.strftime(self.timeformat), 
            'format': self.timeformat,
        }
    
    def encode_Location(self,obj):
        d = {'latitude': obj.latitude, 'longitude': obj.longitude}
        if obj.name:
            d['name'] = obj.name
        return d
    
    def encode_G2SProfile(self,obj):
        return obj.as_dict()

class G2SProfileDecoder(ExtendedDecoder):
    def decode_datetime(self,obj):
        return datetime.strptime(obj['datetime'],obj['format']).replace(tzinfo=timezone.utc)
    
    def decode_Location(self,obj):
        loc = Location(lat=float(obj['latitude']), lon=float(obj['longitude']))
        try:
            loc.name = obj['name']
        except KeyError:
            pass
        return loc
    
    def decode_G2SProfile(self,obj):
        profile = G2SProfile()
        for key, val in obj['metadata'].items():
            profile.set_metadata(key,val)
        for item in obj['data']:
            profile.add_parameter(
                G2SParameter(
                    code=item['parameter'],
                    description=item['description'],
                    units=item['units'],
                    values=[float(x) for x in item['values']],
                )
            )
        return profile
    
    def decode_G2SProfileSet(self,obj):
        profileset = G2SProfileSetFactory.factory.create(obj['metadata']['type'])
        for key, val in obj['metadata'].items():
            profileset.set_metadata(key,val)
        for profile in obj['points']:
            profileset.append(profile)
        profileset.finalize()
        return profileset
        


class G2SFormatter:
    '''Abstract base class for a G2S profile output formatter.
    Accepts a G2SOutput object and returns a formatted version.
    '''
    def __init__(self,*args,**kwargs):
        self.time_format_ = NCPA_G2S_DEFAULT_JSON_TIME_FORMAT
    
    def format(self,profile):
        raise NotImplementedError
    
    def filename(self,profile):
        return f'ncpag2s_{profile.metadata["time"].strftime("%Y%m%d%H%M%S")}_{profile.location.latitude:+08.5f}_{profile.location.longitude:+09.5f}.{self.ext}'
    
    def timestr(self,time):
        return time.astimezone(timezone.utc).strftime(self.time_format_)
    
    def to_file(self,profile,path=None,filename=None,overwrite=False,binary=False):
        if path is None:
            path = '.'
        if filename is None:
            filename = self.filename(profile)
        mode = 'w' if overwrite else 'a'
        mode = f'{mode}b' if binary else f'{mode}t'
        fullfile = os.path.join(path,filename)
        with open(fullfile,mode) as fid:
            fid.write(self.format(profile))
        return fullfile
    

class NCPAPropG2SFormatter(G2SFormatter):
    def __init__(self,*args,**kwargs):
        self.ext = 'ncpaprop'
        super().__init__(*args,**kwargs)
        
    def format_profile(self,profile,*args,**kwargs):
        outputs = []
        headerlines = self.make_header_(profile)
        bodylines = self.make_body_(profile)
        outputs += headerlines
        outputs += bodylines
        return "\n".join(outputs) + "\n"
    
    def format(self,profile,*args,**kwargs):
        typename = type(profile).__name__
        if typename == 'G2SProfile':
            return self.format_profile(profile,*args,**kwargs)
        elif typename == 'G2SProfileLine':
            return self.format_line(profile,*args,**kwargs)
        
        # outputs = []
        # headerlines = self.make_header_(profile)
        # bodylines = self.make_body_(profile)
        # outputs += headerlines
        # outputs += bodylines
        # return "\n".join(outputs) + "\n"
    
    def to_file(self,profile,path=None,filename=None,overwrite=False):
        return super().to_file(profile,path,filename,overwrite,binary=False)
    
    def make_header_(self,profile):
        lines = []
        if profile.get_metadata("sourcefile"):
            lines.append(f'# Data Source: {os.path.split(profile.get_metadata("sourcefile"))[-1]}')
        if profile.get_metadata("calculated_time"):
            lines.append(f'# Model Calculated {self.timestr(profile.get_metadata("calculated_time"))}')
        lines.append(f'# Model Time {self.timestr(profile.get_metadata("time"))}')
        lines.append(f'# Location = [ {profile.location.lat:.4f}, {profile.location.lon:.4f} ]')
        lines.append(f'# Fields = [ Z(km), T(K), U(m/s), V(m/s), R(g/cm3), P(mbar) ]')
        lines.append(f'# Ground Height = {profile.parameters["Z0"].values[0]} {profile.parameters["Z0"].units}')
        lines.append(f'# The following lines are formatted input for ncpaprop')
        lines.append(f'#% 0, Z0, {profile.parameters["Z0"].units}, {profile.parameters["Z0"].values[0]}')
        lines.append(f'#% 1, Z, {profile.parameters["Z"].units}')
        lines.append(f'#% 2, T, {profile.parameters["T"].units}')
        lines.append(f'#% 3, U, {profile.parameters["U"].units}')
        lines.append(f'#% 4, V, {profile.parameters["V"].units}')
        lines.append(f'#% 5, RHO, {profile.parameters["R"].units}')
        lines.append(f'#% 6, P, {profile.parameters["P"].units}')
        return lines
    
    def make_body_(self,profile):
        codes = ['Z','T','U','V','R','P']
        params = profile.get_data_vectors(codes)
        lines = []
        for (z,t,u,v,r,p) in zip(*params):
            lines.append(f'{z:>7.3f} {t:>16.5e}  {u:>16.5e}  {v:>16.5e}  {r:>16.5e}  {p:>16.5e}')
        return lines
        
    def format_line(self,line,output_dir,*args,**kwargs):
        if os.path.exists(output_dir) and not os.path.isdir(output_dir):
            raise FileExistsError(f'{output_dir} exists but is not a directory!')
        os.makedirs(output_dir,exist_ok=True)
        summaryfile = os.path.join(output_dir,'summary.dat')
        if os.path.exists(summaryfile):
            raise FileExistsError(f'{summaryfile} already exists!  Please delete before retrying')
        profiledir = os.path.join(output_dir,'profiles')
        os.makedirs(profiledir,exist_ok=True)
        with open(summaryfile,'wt') as summary:
            for profile in line.get_profiles():
                profile_filename = self.filename(profile)
                self.to_file(profile,path=profiledir,filename=profile_filename,overwrite=True)
                summary.write(f'{profile.get_metadata("range"):.1f}  profiles/{profile_filename}\n')
        
                
    
class JSONG2SFormatter(G2SFormatter):
    def __init__(self,indent=NCPA_G2S_DEFAULT_JSON_INDENT,*args,**kwargs):
        self.indent = indent
        self.ext = 'json'
        super().__init__(*args,**kwargs)
        
    def format(self,profile):
        return json.dumps(profile,indent=self.indent,cls=G2SProfileEncoder) + '\n'
    
    def to_file(self,profile,path=None,filename=None,overwrite=False):
        return super().to_file(profile,path,filename,overwrite,binary=False)
        

# builders
class NCPAPropG2SFormatterBuilder:
    def __init__(self):
        self._instance = None
        
    def __call__(self):
        if not self._instance:
            self._instance = NCPAPropG2SFormatter()
        return self._instance

class JSONG2SFormatterBuilder:
    def __init__(self):
        self._instance = None
        
    def __call__(self):
        if not self._instance:
            self._instance = JSONG2SFormatter()
        return self._instance

# invoke with G2SFormatterFactory.factory.create('ncpaprop')
class G2SFormatterFactory:
    factory = ObjectFactory()
    factory.register_builder('ncpaprop',NCPAPropG2SFormatterBuilder())
    factory.register_builder('json',JSONG2SFormatterBuilder())
    
    
    
class G2SProfileSetJSONIterator:
    def __init__(self,profileset,indent=NCPA_G2S_DEFAULT_JSON_INDENT):
        self.profileset = profileset
        self.indent = indent
        
    def __iter__(self):
        return self
    
    def __next__(self):
        self.stream()
    
    def stream(self,reader):
        yield('{')
        yield('"metadata": ')
        self.profileset.update_metadata()
        yield(json.dumps(self.profileset.metadata,indent=self.indent,cls=G2SProfileEncoder))
        yield(',"points": [')
        sep = ''
        for profile in self.profileset.stream(reader):
            yield(sep + json.dumps(profile,indent=self.indent,cls=G2SProfileEncoder))
            sep = ','
        yield('],"__extended_json_type__": "G2SProfileSet"}\n')
        



