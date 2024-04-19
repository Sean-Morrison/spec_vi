from spec_vi.boss.build_title import build_title
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, Slider
import numpy as np
import sys
import warnings


#keymap.fullscreen: f, ctrl+f   # toggling
#keymap.home: h, r, home        # home or reset mnemonic
#keymap.back: left, c, backspace, MouseButton.BACK  # forward / backward keys
#keymap.forward: right, v, MouseButton.FORWARD      # for quick navigation
#keymap.pan: p                  # pan mnemonic
#keymap.zoom: o                 # zoom mnemonic
#keymap.save: s, ctrl+s         # saving current figure
#keymap.help: f1                # display help about active tools
#keymap.quit: ctrl+w, cmd+w, q  # close the current figure
#keymap.quit_all:               # close all figures
#keymap.grid: g                 # switching on/off major grids in current axes
#keymap.grid_minor: G           # switching on/off minor grids in current axes
#keymap.yscale: l               # toggle scaling of y-axes ('log'/'linear')
#keymap.xscale: k, L            # toggle scaling of x-axes ('log'/'linear')
#keymap.copy: ctrl+c, cmd+c     # copy figure to clipboard

plt.rcParams['keymap.save'].remove('s')
plt.rcParams['keymap.quit'].remove('q')
plt.rcParams['keymap.home'].remove('r')
plt.rcParams['keymap.back'].remove('left')
plt.rcParams['keymap.forward'].remove('right')
plt.rcParams['keymap.fullscreen'].remove('f')


elines= {3727.:'OII', 3869.7867:'NeIII', 4105.8884: r'H$\mathbf{\delta}$',
         4341.6803: r'H$\mathbf{\gamma}$', 4364.3782:'OIII', 4862.6778: r'H$\mathbf{\beta}$',
         4960.2140:'', 5008.1666:'OIII', 5876.:'HeI', 6301.9425:'OI',
         6549.7689:'NII', 6564.6127:r'H$\mathbf{\alpha}$', 6585.1583:'NII',
         6718.1642: '', 6732.5382: 'SII',7137.6370:'ArIII', 2800.:'MgII',
         1216.:r'Ly$\mathbf{\alpha}$', 1549.:'CIV', 1640.:'HeII', 1909.:'CIII',
         2326.:'CII', 1400.:'SiIV+OIV'}


figsize=[8,6]
showmodel = False
show_mask = False
show_ivar = False
def rebin(data,kernel_size ):
    kernel = np.ones(kernel_size) / kernel_size
    return np.convolve(data, kernel, mode='same')

def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
            to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    """
    return  ~np.isfinite(y), lambda z: z.nonzero()[0]




def plot(spec, spall, idx, vi_log, exts = None, allsky=False, field=None,
         smoothing=1):
    global figsize
    global cid
    global showmodel
    global exts_line
    global show_mask
    global show_ivar
    z = spall['Z']
    log_line = str(spall['RACAT'])+' '+str(spall['RACAT'])+' '+'{}'
    #if z<0: return
    fig, ax = plt.subplots(figsize=figsize)
    plt.title(build_title(spall, spall['CATALOGID'],
                          allsky=allsky,field=field),fontsize=10)
    wave = np.power(10,spec['LOGLAM'])/(1+z)
    flux = rebin(spec['FLUX'],smoothing )

    line, = ax.plot(wave, flux,label=idx+1)

    ylim = ax.get_ylim()
    amask = 0.2 if show_mask else 0
    
    def _flag(wave, ivar,sflux, smoothing = 1, alpha = 0):
        igd= np.where((ivar > 0) & (np.abs(wave-5577.) > 4.) & (wave < 10000.) & (wave > 3700.))[0]
        if len(igd) > 0:
            yra= [np.nanmin(sflux[igd]),np.nanmax(sflux[igd])]
        else:
            yra= [np.nanmin(sflux),np.nanmax(sflux)]
        size= 0.07*(yra[1]-yra[0])
        yra=yra+np.array([-1.2,1.7])*size*1000
        if(yra[0] < -2.):
            yra[0]=-1000
        if yra[0] == yra[1]:
            yra=[0,1]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            err= np.sqrt(1/ivar)
            ibad= np.where(ivar <= 0)[0]
            nans, x= nan_helper(err)

            if (len(nans) > 0) and (sum(nans) != len(nans)):
                err[nans]= np.interp(x(nans), x(~nans), err[~nans])

            err = rebin(err, 3)
            #err=sdss_spec_smooth(np.log10(wave), err, 400)
            yerr_u = err.copy()
            yerr_l = err.copy()
            yerr_u[ibad] = yra[1] - sflux[ibad]
            yerr_l[ibad] = sflux[ibad] - yra[0]

        #axs.axvspan(
        fbad1 = ax.fill_between(rebin(wave,2), rebin(sflux-yerr_l,2), rebin(sflux+yerr_u,2),
                        color='k', alpha=alpha, zorder = 1, ec=None, linewidth=0., step='mid')
        fbad2 = ax.fill_between(wave, sflux-yerr_l,sflux+yerr_u, color='k', alpha=alpha,
                         zorder = 1, ec=None, linewidth=0.)
        
        return(fbad1,fbad2)
    
    fbad1, fbad2 = _flag(wave, spec['IVAR'],spec['FLUX'], alpha = amask)
    ax.set_ylim(ylim)
    
    aivar = 1 if show_ivar else 0
    labivar = 'Error' if show_ivar else ''
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        err= np.sqrt(1/spec['IVAR'])
    livar, = ax.plot(wave, err, color='C2',alpha =aivar, label = labivar)
    
    if exts is not None:
        if len(exts) == 0:
            exts = None
        else:
            exts_line = []

            for l, x in enumerate(exts):
                wavex = np.power(10,exts[x]['LOGLAM'])/(1+z)
                fluxx = rebin( exts[x]['FLUX'],smoothing )
                linel, = ax.plot(wavex, fluxx,label=None, alpha = 0, color=f'C{l+3}')
                exts_line.append(linel)
    else:
        exts_line = []
    
    alpha = 1 if showmodel else 0
    label = 'Model' if showmodel else None
    model, = ax.plot(wave, spec['MODEL'],alpha=alpha, color='C1', label=label)
    
    ax.legend()
    for l in elines:
        ax.axvline(l, alpha=.2, color='k', ls= '--')
    ax.set_xlim(min(wave),max(wave))
    if np.nanmax(spec['FLUX']) > np.nanmax(spec['FLUX'][50:])*1.5:
        ax.set_ylim(-1,np.nanmax(spec['FLUX'][50:])*1.5)
    
    ax.set_xlabel('Rest Wavelength $(\mathrm{\AA})$')
    ax.set_ylabel(r'$f_\lambda~(10^{-17}~ergs/s/cm^2/\mathrm{\AA})$')
    fig.subplots_adjust(left=0.25,bottom=0.25,top=.85)

    # Make a horizontal slider to control the redshift.
    zv = fig.add_axes([0.25, 0.08, 0.65, 0.03])
    z_slider = Slider(ax=zv, label='Redshift',
                      valmin=0.0, valmax=7.5, valinit=z)

    # Make a vertically oriented slider to control the smoothing
#    axamp = fig.add_axes([0.1, 0.25, 0.0225, 0.63])
    axamp = fig.add_axes([0.25, 0.135, 0.65, 0.03])
    s_slider = Slider(ax=axamp, label="Smoothing", #orientation="vertical",
                      valmin=1, valmax=20, valinit=smoothing, valstep=1)

    # The function to be called anytime a slider's value changes
    def update(val):
        wave = np.power(10,spec['LOGLAM'])/(1+z_slider.val)
        flux = rebin(spec['FLUX'],s_slider.val )
        #kernel = np.ones(s_slider.val) / s_slider.val
        #flux  = np.convolve(spec['FLUX'], kernel, mode='same')
        line.set_ydata(flux)
        
        dum1, dum2 = _flag(wave, spec['IVAR'],spec['FLUX'], smoothing = 1, alpha = 0)
        dp = dum1.get_paths()[0]
        fbad1.set_paths([dp.vertices])
        dp = dum2.get_paths()[0]
        fbad2.set_paths([dp.vertices])
        dum1.remove()
        dum2.remove()

        livar.set_xdata(wave)

        if exts is not None:
            for l, x in enumerate(exts):
                wavex = np.power(10,exts[x]['LOGLAM'])/(1+z_slider.val)
                flux = rebin(exts[x]['FLUX'],s_slider.val )
                #flux  = np.convolve(exts[x]['FLUX'], kernel, mode='same')
                exts_line[l].set_ydata(flux)

        line.set_xdata(wave)
        mwave = np.power(10,spec['LOGLAM'])/(1+z)#*(1+z)
        model.set_xdata(mwave)

        ax.set_xlim(min(wave),max(wave))
        fig.canvas.draw_idle()

    # register the update function with each slider
    z_slider.on_changed(update)
    s_slider.on_changed(update)

    # Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
    resetax = fig.add_axes([0.02, 0.025, 0.1, 0.04])
    button = Button(resetax, 'Reset', hovercolor='0.975')
 
    resetax = fig.add_axes([0.02, 0.08, 0.1, 0.04])
    modelbutton = Button(resetax, 'Model', hovercolor='0.975')
 
    if exts is not None:
        resetax = fig.add_axes([0.02, .94, 0.1, 0.04])
        Extbutton = Button(resetax, 'Extensions', hovercolor='0.975')

    resetax = fig.add_axes([0.02, 0.135, 0.1, 0.04])
    maskbutton = Button(resetax, 'Show Mask', hovercolor='0.975')

    resetax = fig.add_axes([0.02, 0.19, 0.1, 0.04])
    ivarbutton = Button(resetax, 'Show Error', hovercolor='0.975')

    resetax = fig.add_axes([0.15, 0.025, 0.15, 0.04])
    buttonnext= Button(resetax, 'next+save', hovercolor='0.975')

    resetax = fig.add_axes([0.30, 0.025, 0.15, 0.04])
    buttonnonqso= Button(resetax, 'next+nonqso', hovercolor='0.975')

    resetax = fig.add_axes([0.49, 0.025, 0.18, 0.04])
    buttonq = Button(resetax, 'exit (no save)', hovercolor='0.975')
    
    resetax = fig.add_axes([0.67, 0.025, 0.15, 0.04])
    buttonsx = Button(resetax, 'Save & Exit', hovercolor='0.975')

    resetax = fig.add_axes([0.82, 0.025, 0.17, 0.04])
    buttonsx = Button(resetax, 'nonqso & Exit', hovercolor='0.975')

    def reset(event):
        z_slider.reset()
        s_slider.reset()
    button.on_clicked(reset)

    def setmodel(event):
        global showmodel
        if model.get_alpha() == 0:
            model.set_alpha(1)
            model.set_label('Model')
            showmodel = True
        else:
            model.set_alpha(0)
            model.set_label(None)
            showmodel = False
        ax.legend()
        fig.canvas.draw_idle()
    modelbutton.on_clicked(setmodel)

    def setMask(event):
        global show_mask
        if fbad1.get_alpha() == 0:
            fbad1.set_alpha(.2)
            fbad2.set_alpha(.2)
            show_mask = True
        else:
            fbad1.set_alpha(0)
            fbad2.set_alpha(0)
            show_mask = False
        ax.legend()
        fig.canvas.draw_idle()
    maskbutton.on_clicked(setMask)

    def setIvar(event):
        global show_ivar
        if livar.get_alpha() == 0:
            livar.set_alpha(1)
            livar.set_label('ivar')
            show_ivar = True
        else:
            livar.set_alpha(0)
            show_ivar = False
            livar.set_label(None)
        ax.legend()
        fig.canvas.draw_idle()
    ivarbutton.on_clicked(setIvar)


    def setExt(event):
        global exts_line
        if exts is not None:
            for l, ll in enumerate(exts_line):
                if ll.get_alpha() == 0:
                    ll.set_alpha(1)
                    ll.set_label(f'exp:{list(exts.keys())[l]}',)
                else:
                    ll.set_alpha(0)
                    ll.set_label(None)
            ax.legend()
            fig.canvas.draw_idle()
    if exts is not None:
        Extbutton.on_clicked(setExt)

    def savequit(event):
        vi_log.log(log_line.format(z_slider.val))
        vi_log.close()
        exit()
    buttonsx.on_clicked(savequit)

    def quit(event):
        exit()
    buttonq.on_clicked(quit)

    def next(event):
        global figsize
        if z != z_slider.val:
            vi_log.log(log_line.format(z_slider.val))
        figsize = fig.get_size_inches()
        plt.close()
        return
    buttonnext.on_clicked(next)

    def nextnoqso(event):
        global figsize
        vi_log.log(log_line.format('nonqso'))
        figsize = fig.get_size_inches()
        plt.close()
    buttonnonqso.on_clicked(nextnoqso)

    def pan_nav(event):
        global figsize
        global cid
        global showmodel
        global exts_line
        global show_mask
        if event.key == 'r':
            z_slider.reset()
        elif event.key == 'q':
            vi_log.close()
            exit()
        elif event.key == 'e':
            if z != z_slider.val:
                vi_log.log(log_line.format(round(z_slider.val,3)))
            vi_log.close()
            exit()
        elif event.key == 'x':
            vi_log.log(log_line.format('nonqso'))
            vi_log.close()
            exit()
        elif event.key == '+' or event.key == 'up':
            if s_slider.val < 20:
                s_slider.eventson = False
                s_slider.set_val(s_slider.val + 1)
                fig.canvas.draw()
                s_slider.eventson = True
                update(s_slider.val )
        elif event.key == '-' or event.key == 'down':
            if s_slider.val >1:
                s_slider.eventson = False
                s_slider.set_val(s_slider.val - 1)
                fig.canvas.draw()
                s_slider.eventson = True
                update(s_slider.val )
        elif event.key == 's':
            vi_log.log(log_line.format(round(z_slider.val,3)))
            figsize = fig.get_size_inches()
            plt.close()
        elif event.key == 'n':
            vi_log.log(log_line.format('nonqso'))
            figsize = fig.get_size_inches()
            plt.close()
        elif event.key == 'left':
            z_slider.eventson = False
            z_slider.set_val(z_slider.val - .005)
            fig.canvas.draw()
            z_slider.eventson = True
            update(z_slider.val)
        elif event.key == 'right':
            z_slider.eventson = False
            z_slider.set_val(z_slider.val + .005)
            fig.canvas.draw()
            z_slider.eventson = True
            update(z_slider.val)
        elif event.key == 'z':
            fig.canvas.mpl_disconnect(cid)
            test = input('Select Terminal and enter redshift: ')
            cid = fig.canvas.mpl_connect('key_press_event', pan_nav)
            z_slider.eventson = False
            z_slider.set_val(float(test))
            fig.canvas.draw()
            z_slider.eventson = True
            update(z_slider.val)
            sys.stdout.write("\033[F") # Cursor up one line
            sys.stdout.write('                                                   ')
            sys.stdout.write("\033[F") # Cursor up one line
            sys.stdout.flush()
            sys.stdout.write("\n")
            sys.stdout.flush()
        elif event.key == 'm':
            if model.get_alpha() == 0:
                model.set_alpha(1)
                model.set_label('Model')
                showmodel = True
            else:
                model.set_alpha(0)
                model.set_label(None)
                showmodel = False
            ax.legend()
            fig.canvas.draw_idle()
        elif event.key == 'f':
            if exts is not None:
                for l, ll in enumerate(exts_line):
                    if ll.get_alpha() == 0:
                        ll.set_alpha(1)
                        ll.set_label(f'exp:{list(exts.keys())[l]}',)
                    else:
                        ll.set_alpha(0)
                        ll.set_label(None)
                ax.legend()
                fig.canvas.draw_idle()
        elif event.key == 'b':
            if fbad1.get_alpha() == 0:
                fbad1.set_alpha(.2)
                fbad2.set_alpha(.2)
                show_mask = True
            else:
                fbad1.set_alpha(0)
                fbad2.set_alpha(0)
                show_mask = False
            ax.legend()
            fig.canvas.draw_idle()
        elif event.key == 'i':
            global show_ivar
            if livar.get_alpha() == 0:
                livar.set_alpha(1)
                livar.set_label('Error')

                show_ivar = True
            else:
                livar.set_alpha(0)
                show_ivar = False
                livar.set_label(None)
            ax.legend()
            fig.canvas.draw_idle()

    cid = fig.canvas.mpl_connect('key_press_event', pan_nav)
    plt.show(block=True)
    return
