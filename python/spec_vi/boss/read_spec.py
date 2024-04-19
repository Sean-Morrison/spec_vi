from astropy.io import fits
from collections import OrderedDict
from astropy.table import Table
import warnings

def read_spec(file, full = False):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hdul = fits.open(file, memmap=False)
        spec  = Table(hdul[1].data)
        spall = Table(hdul[2].data)
        if full:
            exts = OrderedDict()
            for x in hdul[5:]:
                exts[x.header['EXPOSURE']] = x.data
        else:
            exts = None
        hdul.close()
        hdul = None
    return(spec,spall, exts)
