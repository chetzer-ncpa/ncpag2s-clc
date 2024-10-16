from ncpa.g2scli import G2SClient
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import numpy as np

client = G2SClient()
t = datetime(2024,10,15,0,tzinfo=timezone.utc)
lat1 = 19.59
lon1 = -155.89
lat2 = 64.84
lon2 = -147.72
npts = 51

# Get a point profile
profile = client.point(time=t,latitude=lat1,longitude=lon1)

# Some basic info
print(' '.join((
    f'Downloaded profile for [{profile.location.latitude},{profile.location.longitude}]',
    f'at {profile.time.strftime("%Y-%m-%d %H:00:00")}'))
    )
z0 = profile.parameters["Z0"]
print(f'Ground height is {z0.values[0]} {z0.units}')

fig, ax = plt.subplots(1,5,sharey=True,figsize=(11,6))
fig.subplots_adjust(hspace=0.05,wspace=0.05)
Z = profile.parameters["Z"].values
for i, param in enumerate(['T','U','V','P','R']):
    if param in ('P','R'):
        ax[i].semilogx(profile.parameters[param].values,Z)
    else:
        ax[i].plot(profile.parameters[param].values,Z)
    ax[i].set_title(f'{param} [{profile.parameters[param].units}]')
    ax[i].grid(linestyle='--')
    ax[i].set_ylim(0,150.0)

ax[0].set_ylabel('Altitude [km]')
fig.suptitle(f'[{profile.location.latitude},{profile.location.longitude}] at {profile.time.strftime("%Y-%m-%d %H:00:00")}')
plt.show()
plt.close()

# Get a line profile
line = client.line(time=t,start=(lat1,lon1),end=(lat2,lon2),points=npts)
nz = len( line.profiles[0].parameters['Z'].values )
rmax = line.range_to(line.profiles[-1])

Tslice = np.ndarray((nz,npts))
Uslice = np.ndarray((nz,npts))
Vslice = np.ndarray((nz,npts))
for i, profile in enumerate(line.profiles):
    Tslice[:,i] = profile.parameters['T'].values
    Uslice[:,i] = profile.parameters['U'].values
    Vslice[:,i] = profile.parameters['V'].values

fig, (Tax, Uax, Vax) = plt.subplots(nrows=3, sharex=True, figsize=(12,6))
Tax.imshow(Tslice, extent=[0,rmax,0,150], aspect='auto')
Tax.set_title('Temperature [K]')
Uax.imshow(Uslice, extent=[0,rmax,0,150], aspect='auto')
Uax.set_title('U Winds [m/s]')
Vax.imshow(Vslice, extent=[0,rmax,0,150], aspect='auto')
Vax.set_title('V Winds [m/s]')
plt.tight_layout()
plt.show()
    
    
    
    
     
