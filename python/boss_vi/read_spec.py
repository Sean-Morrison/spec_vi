from astropy.io import fits
from collections import OrderedDict
from astropy.table import Table

def read_spec(file, full = False):
    with fits.open(file) as hdul:
        spec  = hdul[1].data
        spall = hdul[2].data
        if full:
            exts = OrderedDict()
            for x in hdul[5:]:
                exts[x.header['EXPOSURE']] = x.data
        else:
            exts = None
    return(spec,Table(spall)[0], exts)
