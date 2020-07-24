# decompress a .tar.gz archive and convert to a gzip .sqfs archive
# decompresses and squashes sequentially since squashfs itself can execute in parallel

import sys
import os
import subprocess
import shutil

base_dir = sys.argv[1].strip()
file_list = sys.argv[2]
#squash_dir = sys.argv[3]
if len(sys.argv) == 5:
    delete_tar = sys.argv[4]
    if delete_tar.lower() == 'true':
        delete_tar = True
    else:
        delete_tar = False
else:
    delete_tar = False

file_list_fd = open(file_list, 'r')
for line in file_list_fd:
    spl = line.split(' ')
    if len(spl) == 2:
        fn = spl[1].strip()
    elif len(spl) == 1:
        fn = spl[0].strip()
    else:
        assert False # bad format
    tarball = base_dir + fn
    # check that it is actually a gzipped tarball
    spl = tarball.split('.')
    if len(spl) > 2:
        tail = spl[-1]
        tail_m1 = spl[-2]
        if tail == 'gz':
            assert tail_m1 == 'tar'
            tarball_no_sfx = '.'.join(spl[0:-2])
        else:
            assert tail == 'tgz'
            tarball_no_sfx = '.'.join(spl[0:-1])
    else:
        assert spl[-1] == '.tgz'
        tarball_no_sfx = '.'.join(spl[0:-1])
    # untar/decompress
    untardir = '/'.join(tarball_no_sfx.split('/')[0:-1])
    untar_args = ['tar', '-C', untardir, '-xzf', tarball]
    print('Running: ' + ' '.join(untar_args))
    subprocess.run(untar_args, check=True, stdout=subprocess.PIPE)
    # squash
    squash_args = ['mksquashfs', tarball_no_sfx, tarball_no_sfx + '.sqfs', '-no-duplicates', '-info']
    print('Running: ' + ' '.join(squash_args))
    subprocess.run(squash_args, check=True, stdout=subprocess.PIPE)
    if delete_tar:
        print('removing ' + tarball)
        os.remove(tarball)
    print('removing ' + tarball_no_sfx)
    shutil.remove(tarball_no_sfx)
file_list_fd.close()
