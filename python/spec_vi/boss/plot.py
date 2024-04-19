from spec_vi.boss.build_title import build_title
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, Slider
import numpy as np
import sys

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

def plot(spec, spall, idx, vi_log, exts = None, allsky=False, field=None):
    global figsize
    global cid
    global showmodel
    global exts_line
    z = spall['Z']
    log_line = str(spall['RACAT'])+' '+str(spall['RACAT'])+' '+'{}'
    #if z<0: return
    fig, ax = plt.subplots(figsize=figsize)
    plt.title(build_title(spall, spall['CATALOGID'],
                          allsky=allsky,field=field),fontsize=10)
    wave = np.power(10,spec['LOGLAM'])/(1+z)
    line, = ax.plot(wave, spec['FLUX'],label=idx+1)
    
    if exts is not None:
        if len(exts) == 0:
            exts = None
        else:
            exts_line = []

            for l, x in enumerate(exts):
                wavex = np.power(10,exts[x]['LOGLAM'])/(1+z)
                linel, = ax.plot(wavex, exts[x]['FLUX'],label=None, alpha = 0, color=f'C{l+2}')
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
    axamp = fig.add_axes([0.1, 0.25, 0.0225, 0.63])
    s_slider = Slider(ax=axamp, label="Smoothing", orientation="vertical",
                      valmin=1, valmax=20, valinit=1, valstep=1)

    # The function to be called anytime a slider's value changes
    def update(val):
        wave = np.power(10,spec['LOGLAM'])/(1+z_slider.val)
        kernel = np.ones(s_slider.val) / s_slider.val
        flux  = np.convolve(spec['FLUX'], kernel, mode='same')
        line.set_ydata(flux)
        
        if exts is not None:
            for l, x in enumerate(exts):
                wavex = np.power(10,exts[x]['LOGLAM'])/(1+z_slider.val)
                flux  = np.convolve(exts[x]['FLUX'], kernel, mode='same')
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
        resetax = fig.add_axes([0.02, 0.135, 0.1, 0.04])
        Extbutton = Button(resetax, 'Extensions', hovercolor='0.975')

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

    cid = fig.canvas.mpl_connect('key_press_event', pan_nav)
    plt.show(block=True)
    return
