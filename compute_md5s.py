# recursively go thru a directory and compute the md5s of individual files.
import os
import sys
import subprocess
import shutil
from pathlib import Path

base_dir = sys.argv[1]
output_md5_file = sys.argv[2]
output_fd = open(output_md5_file, 'w')
for f in Path(base_dir).rglob('*.*'):
    if os.path.isfile(f):
        md5_args = ['md5sum', f]
        res = subprocess.run(md5_args, check=True, stdout=subprocess.PIPE)
        output_fd.write(str(res.stdout, 'utf-8'))
        output_fd.flush()
output_fd.close()
        
