from spec_vi.boss.plot import plot
from spec_vi.boss.read_spec import read_spec
from spec_vi import VI_log
from os import getenv
import os.path as ptt
from glob import glob

def boss_vi(chunkfile = None, logfile = None, append = False,
            start = None, download = False, epoch = False,
            manual = None, full = False, allepoch = False,
            smoothing = 1):
            
    vi_log = VI_log(logfile, append = append)

    print("Press 's' to move to next image saving redshift")
    print("      'n' to move to next image flagging as nonqso")
    print("      'q' to exit without saving current spectra")
    print("      'x' to exit with marking as nonqso")
    print("      'e' to exit with saving current redshift value")
    print("      'r' to reset to spAll redshift")
    print(u"      '+' or '\u2191' to increase smoothing by 1")
    print(u"      '-' or '\u2193' to decrease smoothing by 1")
    print(u"      '\u2190' to decrease redshift by 0.005")
    print(u"      '\u2192' to increase redshift by 0.005")
    print("      'z' to manually enter redshift in the terminal")
    print("      'm' to toggle the model fit (shifted to rest frame)")
    print("      'b' to toggle the mask (shifted to rest frame)")
    print("      'i' to toggle the Errors (shifted to rest frame)")
    if full:
        print("      'f' to toggle to individual exposures")

    if manual is None:
        chunk = fits.getdata(chunkfile)
        
        type = 'specLite'
        if epoch:
            type = type+'_epoch'
        elif allepoch:
            type = type+'_coadd'
        if full:
            type = type.replace('Lite','Full')

        if download:
            try:
                access.remote()
            except:
                raise Exception("ERROR: No netrc file found. see https://sdss-access.readthedocs.io/en/latest/auth.html#auth")
                exit()
        
            access.remote()
            cnt = 0
            for row in chunk:
                if not allepoch:
                    target_kwrds = {'run2d':row['RUN2D'], 'fieldid':row['FIELD'],
                                    'mjd':row['MJD'], 'catalogid':row['CATALOGID']}
                else:
                    coadd = 'allepoch' if row['OBS'] else 'allepoch_lco'
                    target_kwrds = {'coadd':coadd, 'run2d':row['RUN2D'],
                                    'mjd':row['MJD'], 'catalogid':row['CATALOGID']}
                if path.exists(type, remote=True, **target_kwrds):
                    #check if file exists locally
                    if access.exists(type, **target_kwrds):
                        print('skipping '+access.find_location(type, **target_kwrds)+' (exists)')
                    else:
                        access.add(type, **target_kwrds)
                        cnt += 1
            if cnt >0:
                access.set_stream()
                access.commit()
        
        for i,row in enumerate(chunk):
            if start is not None:
                if i < start: continue
            if row['OBJTYPE'].lower() != 'science':
                continue
            try:
                sf = 'full' if full else 'lite'
                se = 'epoch' if epoch else ''
                if not allepoch:
                    field = str(row['FIELD']).zfill(6)
                else:
                    field = 'allepoch' if row['OBS'] else 'allepoch_lco'

                file = ptt.join(getenv('BOSS_SPECTRO_REDUX'),row['RUN2D'],se,
                                'spectra',sf,field,str(row['MJD']),
                                row['SPEC_FILE'])
                spec, spall, exts = read_spec(file,full=full)
            except:
                if not allepoch:
                    target_kwrds = {'run2d':row['RUN2D'], 'fieldid':row['FIELD'],
                                    'mjd':row['MJD'], 'catalogid':row['CATALOGID']}
                    field = row['FIELD']
                else:
                    field = 'allepoch' if row['OBS'] else 'allepoch_lco'
                    target_kwrds = {'coadd':field, 'run2d':row['RUN2D'],
                                'mjd':row['MJD'], 'catalogid':row['CATALOGID']}
                file = path.full(type,**target_kwrds)
                spec, spall, exts = read_spec(file, full=full)
            plot(spec,spall, i, vi_log, exts=exts, allsky = allepch,
                 field=field, smoothing=smoothing)
    else:
        files = glob(manual)
        for i, file in enumerate(files):
            if start is not None:
                if i < start: continue
            spec, spall, exts = read_spec(file, full= full)
            if spall['FIELD'] == 0:
                field = 'allepoch' if spall['OBS'] else 'allepoch_lco'
                allsky = True
            else:
                field = spall['FIELD']
                allsky = False
            plot(spec,spall,i, vi_log, exts = exts, allsky=allsky,
                 field=field, smoothing=smoothing)

    vi_log.close()
