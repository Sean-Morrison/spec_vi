from pydl.pydlutils.sdss import sdss_flagname


def build_title(spAll):

    survey = spAll['SURVEY'].strip().replace('_','\_')
    program = spAll['PROGRAMNAME'].strip().replace('_','\_')

    if 'SDSS_ID' in spAll.columns:
        SDSSID = spAll['SDSS_ID']
        if ((SDSSID == -999) or (SDSSID == -1) or (SDSSID == 0)): SDSSID = ''
    else:
        SDSSID = None

    field = spAll['FIELD']
    legacy = False if int(field)>=15000 else True
    plates = False if int(field)>=16000 else True
    sfield = str(spAll['FIELD'])

    #ptitle = r'Survey: $'+survey+r'$, Program: $'+program+r'$, '
    
    try:
        obs =spAll['OBS'].strip()
    except:
        obs = ''
    obstitle = r'Observatory: '+obs+r', '
    ptitle = r'Program: $'+program+r'$, '

    if survey == 'sdss':
        targ_title='Target'
        primtarget = spAll['PRIMTARGET']
        targets= ' '.join(sdss_flagname('TARGET', primtarget))
    elif survey == 'segue1':
        targ_title='Target'
        primtarget = spAll['PRIMTARGET']
        targets= ' '.join(sdss_flagname('SEGUE1_TARGET', primtarget))
    elif survey ==  'boss':
        targ_title='Target'
        boss_target1 = spAll['BOSS_TARGET1']
        ANCILLARY_TARGET1 = spAll['ANCILLARY_TARGET1']
        targets= ' '.join(sdss_flagname('BOSS_TARGET1', boss_target1))+ ' '+ ' '.join(sdss_flagname('ANCILLARY_TARGET1', ANCILLARY_TARGET1))
    elif ((survey.lower() in ['bhm-mwm', 'bhm', 'mwm', 'mwm-bhm','open\_fiber'])):
        targ_title='Firstcarton'
        targets= spAll['FIRSTCARTON'].replace('_','\_')
    else:
        targ_title = ''
        targets = 'NA'
    if targets.strip() == 'NA':
        targ_title='Firstcarton'
        targets=str(spAll['OBJTYPE']).strip().replace('_','\_')

    ptitle= ptitle+targ_title+r': $'+targets+r'$'

    if not legacy:
        if SDSSID is not None:
            ptitle = ptitle+ '\n '
            ptitle = ptitle+ 'SDSS_ID='+str(SDSSID)
        catid = spall['CATALOGID'][0]
        ptitle = ptitle+', '+'CatID='+str(catid)+ '\n '
    else:
        if SDSSID is not None:
            ptitle = ptitle+', '+'SDSS_ID='+str(SDSSID)+ '\n '
        else:
            ptitle = ptitle+ '\n '

    if 'FIBER_RA' in spAll.columns:
        title1= ('RA='+"%.5f" % spAll['FIBER_RA']+', '+'Dec='+"%.5f" % spAll['FIBER_DEC']+', '+
                 'Field='+sfield+', '+obstitle+'TargetIndex='+str(spAll['TARGET_INDEX'])+', '+
                 'MJD='+str(spAll['MJD']))
    else:
        title1= ('RA='+"%.5f" % spAll['PLUG_RA']+', '+'Dec='+"%.5f" % spAll['PLUG_DEC']+', '+
                 'Field='+sfield+', '+obstitle+'Fiber='+str(spAll['FIBERID'])+', '+
                 'MJD='+str(spAll['MJD']))
    ptitle = ptitle + title1+'\n'

    if(spAll['Z'] < 1000./299792.):
        zstr= r'$cz=$'+str(int(spAll['Z']*299792.))+r'$\pm$'+str(int(spAll['Z_ERR']*299792.))+' km/s'
    else:
        zstr= r'$z=$'+"%.5f" % spAll['Z']+r'$\pm$'+"%.5f" % spAll['Z_ERR']
        
    title2 = zstr+', Class='+spAll['CLASS'].strip()+' '+spAll['SUBCLASS'].strip()
    if len(spAll['SUBCLASS'].strip()) == 0:
        title2 = zstr+', Class='+spAll['CLASS'].strip()

    
    mag_vec=spAll['FIBER2MAG']
    m_i=mag_vec[3]
    title2=title2+r', mag$_{i,fib2}$='+"%.2f" % m_i
    
    ptitle = ptitle + title2+'\n'

    if spAll['ZWARNING'] > 0:
        warnings= ' '.join(sdss_flagname('ZWARNING', spAll['ZWARNING']))
        title3= 'Warnings: '+warnings
    else:
        title3='No warnings'
    title3 = title3+', idlspec2d='+spAll['RUN2D']
    ptitle = ptitle + title3
    
    ptitle = ptitle.replace(r'$$',r'')
    return(ptitle)
    
