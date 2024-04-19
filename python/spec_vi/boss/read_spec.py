from astropy.io import fits
from collections import OrderedDict
from astropy.table import Table

def read_spec(file, full = False):
    hdul = fits.open(file, memmap=False)
    spec  = Table(hdul[1].data)
    spall = Table(hdul[2].data)[0]
    if full:
        exts = OrderedDict()
        for x in hdul[5:]:
            exts[x.header['EXPOSURE']] = x.data
    else:
        exts = None
    hdul.close()
    hdul = None
    return(spec,spall, exts)
