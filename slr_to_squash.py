# this converts an SLR directory to a squash archive. It is a little different because it doesn't
# come in a single archive format originally--instead it is some zips and tsv files.
# This script unzips the zip files and then shoves everything in a squash archive

import sys
import os
import subprocess

slr_base = sys.argv[1] # where the SLR subdirs are located. should end in '/'
slr_dirs = sys.argv[2] # list something like 61/, 62/, etc. Assumes the structure is slr_base/slr_dir
delete_files = bool(sys.argv[3])

assert slr_base[-1] == '/'

l = lambda d: slr_base + d.strip()
slr_dir_fd = open(slr_dirs, 'r')
full_slr_dirs = [l(d) for d in slr_dir_fd]
slr_dir_fd.close()

for d in full_slr_dirs:
    files = os.listdir(d)
    files = [f for f in files if os.path.isfile(d + '/' + f)]
    to_squash = []
    deletable = []
    for f in files:
        if f.split('.')[-1] == 'zip':
            unzip_args = ['unzip', d + '/' + f, '-d', d + '/' + '.'.join(f.split('.')[0:-1])]
            print('Unzipping: ' + ' '.join(unzip_args))
            subprocess.run(unzip_args, check=True)
            to_squash.append(d + '/' + '.'.join(f.split('.')[0:-1]))
            deletable.append(d + '/' + '.'.join(f.split('.')[0:-1]))
        else:
            to_squash.append(d + '/' + f)
        deletable.append(d + '/' + f)
    squash_out = d + '/' + d.split('/')[-1] + '.sqfs'
    squash_args = ['mksquashfs'] + to_squash + [squash_out]
    print('Running: ' + ' '.join(squash_args))
    subprocess.run(squash_args, check=True)
    if delete_files:
        for s in deletable:
            print('deleting: ' + s)
            os.remove(s)
