#!/usr/bin/env python3

import argparse
from spec_vi.boss import boss_vi
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Visual Inspection Tool for BOSS QSOs')
    parser.add_argument('chunkfile', help='Name of the chunk file (if manual use None')
    parser.add_argument('--logfile','-l', required=False, default='VI_log.dat', help='Name of VI Log')
    parser.add_argument('--append','-a',  required=False, action='store_true',  help='Append to old logfile')
    parser.add_argument('--start', '-s',  required=False, type=int,             help='Skip first n spectra and start with n+1', )
    parser.add_argument('--download','-d',required=False, action='store_true',  help='Use SDSS_access to download the files')
    parser.add_argument('--epoch','-e',   required=False, action='store_true',  help='Use the epoch version of the specLite files')
    parser.add_argument('--manual','-m',  required=False, default=None,         help='Use all spec Files matching this string (with wildcards)')
    parser.add_argument('--full','-f',    required=False, action='store_true',  help='Use SpecFull files if available')
    parser.add_argument('--allepoch','-c',required=False, action='store_true',  help='Use all Epoch Spec files')
    args = parser.parse_args()

    boss_vi(**vars(args))
