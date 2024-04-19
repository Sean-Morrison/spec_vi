This package is designed to assist with visual Inspection of Spectra. At present, only the SDSS-V BOSS tools are available.

# To Install
To use add the location of the spec_vi/python directory to your PYTHONPATH and spec_vi/bin to your $PATH.
It requires a number of python packages
- astropy
- matplotlib
- numpy
- pydl
- sdsstools
- sdss_access

## Running at Utah
For SDSS-V members with Utah accounts, the package is already installed and can be loaded with the spec_vi module


# Running the BOSS Visual Inspection
The BOSS VI tool can be run with
```python
boss_vi.py
```


```

usage: boss_vi.py [-h] [--logfile LOGFILE] [--append] [--start START] [--download] [--epoch]
                  [--manual MANUAL] [--full] [--allepoch] [--smoothing SMOOTHING] chunkfile

Visual Inspection Tool for BOSS QSOs

positional arguments:
  chunkfile             Name of the chunk file (if manual use None)

options:
  -h, --help            show this help message and exit
  --logfile LOGFILE, -l LOGFILE
                        Name of VI Log
  --append, -a          Append to old logfile
  --start START, -s START
                        Skip first n spectra and start with n+1
  --download, -d        Use SDSS_access to download the files
  --epoch, -e           Use the epoch version of the specLite files
  --manual MANUAL, -m MANUAL
                        Use all spec Files matching this string (with wildcards)
  --full, -f            Use SpecFull files if available
  --allepoch, -c        Use all Epoch Spec files
  --smoothing SMOOTHING
                        Set Default Smoothing value (default:1)

```

The chunckfile should be in the same format as the SDSS-V spAll (or spAll-lite) file.
The files can be manually downloaded and placed in a directory structure matching that of the files on the SAS for running with a chunkfile.
Additionally, the user can use the --download flag, combined with sdss_access to automatically download the files within the chunkfile.
Alternatively, the user can save all the files into a directory and use the manual flag with the path to the directory (eg '~/Downloads/chunk/spec-??????-*.fits'.
The code produces a space-separated file of the format: ra dec note.

The code has several interactive options that can be run either by keyboard input (with the shortcuts shown in the terminal) or via the buttons and sliders in the GUI window.
