import h5py
import numpy as np


def pick_events(infiles, outfile):

    fout = h5py.File(outfile, 'w')

    for fname in infiles:

        with h5py.File(fname, 'r') as fin:

            dataset = fin.get('data')
            

    fout.close()
