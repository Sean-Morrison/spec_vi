from spec_vi.boss.plot import plot
from spec_vi.boss.read_spec import read_spec
from spec_vi import VI_log
from os import getenv
import os.path as ptt
from glob import glob
from astropy.io import fits

from sdss_access import Access
from sdss_access.path import Path
access = Access(release='sdsswork')
path = Path(release='sdsswork')


def phelp(full=False):
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
    return


def fix_master_spall(spall, file):
    spall['FIELD'] = ptt.basename(file).split('-')[1]
    spall['RACAT'] = [spall['PLUG_RA']]
    spall['DECCAT'] = [spall['PLUG_DEC']]
    spall['SURVEY'] = ''
    spall['PROGRAMNAME'] = ''
    spall['FIBER2MAG'] = spall['MAG']
    spall['RUN2D'] =  spall['RUN2D'].astype(object)
    spall['RUN2D'] = ['master_plate']
    return(spall)

def boss_vi(chunkfile = None, logfile = None, append = False,
            start = None, download = False, epoch = False,
            manual = None, full = False, allepoch = False,
            smoothing = 1):
            
    vi_log = VI_log(logfile, append = append)

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
                if row['RUN2D'].lower() == 'master':
                    if int(row['FIELD']) < 16000:
                        row['RUN2D'] = 'master_plate'
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
                        print('Adding '+access.find_location(type, **target_kwrds))
                        access.add(type, **target_kwrds)
                        cnt += 1
            if cnt >0:
                print('Downloading')
                access.set_stream()
                access.commit()
                print('Downloading Complete')
        
        phelp(full=full)
        for i,row in enumerate(chunk):
            if start is not None:
                if i < start: continue
            if row['OBJTYPE'].lower() != 'science':
                continue
            if row['RUN2D'].lower() == 'master':
                if int(row['FIELD']) < 16000:
                    row['RUN2D'] = 'master_plate'
            try:
                sf = 'full' if full else 'lite'
                se = 'epoch' if epoch else ''
                if not allepoch:
                    if row['RUN2D'] == 'master_plate':
                        field = str(row['FIELD'])+'p'
                    else:
                        field = str(row['FIELD']).zfill(6)
                else:
                    field = 'allepoch' if row['OBS'] else 'allepoch_lco'

                try:
                    file = row['SPEC_FILE']
                except:
                    file = ('spec-'+row['FIELD']+'-'+row['MJD']+'-'+
                            str(row['CATALOGID']).zfill(11)+'.fits')
                file = ptt.join(getenv('BOSS_SPECTRO_REDUX'),row['RUN2D'],se,
                                'spectra',sf,field,str(row['MJD']),file)
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
            
            try:
                spall['RACAT']
            except:
                fix_master_spall(spall, file)
            spall = spall[0]
            pp = plot(spec,spall, i, vi_log, exts=exts, allsky = allepoch,
                      field=field, smoothing=smoothing)
            spec = None
            spall = None
            exts = None
            pp = None
    else:
        phelp(full=full)
        files = glob(manual)
        for i, file in enumerate(files):
            if start is not None:
                if i < start: continue
            spec, spall, exts = read_spec(file, full= full)
            try:
                if spall['FIELD'][0] == 0:
                    field = 'allepoch' if spall['OBS'][0] else 'allepoch_lco'
                    allsky = True
                else:
                    field = spall['FIELD'][0]
                    allsky = False
            except:
                spall['FIELD'][0] = ptt.basename(file).split('-')[1]
                allsky = False
                field = spall['FIELD'][0]
            try:
                spall['RACAT']
            except:
                fix_master_spall(spall, file)
            spall=spall[0]
            pp = plot(spec,spall,i, vi_log, exts = exts, allsky=allsky,
                      field=field, smoothing=smoothing)
            spec = None
            spall = None
            exts = None
            pp = None
    vi_log.close()
