# Python 3.6.9 (module anaconda3-2019b)
import sys
import subprocess
import math
import os
import hashlib

chunk_size_gb=9.5

base_url = sys.argv[1]
if base_url[-1] != '/':
    base_url += '/'
# list of files with format: [<MD5> ]<relative file path>
# the MD5 is optional
file_list = sys.argv[2]
files = {} # {file_name -> (size, md5)}
file_list_fd = open(file_list, 'r')
for line in file_list_fd:
    spl = line.split(' ')
    if len(spl) == 2:
        md5 = spl[0]        
        fn = spl[1].strip()
    elif len(spl) == 1:
        md5 = None
        fn = spl[0]
    else:
        assert False # bad format
    # user curl to figure out the size (in bytes) of the file
    curl_args = ['curl', '-sI', base_url + fn]
    header = subprocess.run(curl_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    nbytes = -1
    for entry in str(header.stdout, 'utf-8').split('\r\n'):
        spl = entry.split(':')
        if spl[0] == 'Content-Length':
            nbytes = int(spl[1].strip())
            break
    assert nbytes >= 0
    print(nbytes)
    files[fn] = (nbytes, md5)
file_list_fd.close()

# now split up the files into 9.5GB chunks (10GB is the upper limit that can cause issues)
file_chunks = {} # {file_name -> [list of chunk ranges]}
max_bytes = math.floor(chunk_size_gb * 1024 * 1024 * 1024)
for fn,(sz,_) in files.items():
    print(fn)
    chunks = []
    for b in range(0, sz, max_bytes):
        lower = b
        upper = min(lower+max_bytes-1, sz)
        chunks.append((lower, upper))
    file_chunks[fn] = chunks
print(file_chunks)    
        

# download the chunks and reassemble
output_dir = '/home/gridsan/groups/data_corpora_shared/snakers4/'
for fn,chunks in file_chunks.items():
    md5 = files[fn][1]
    chunk_fns = []
    print('Curling: ' + fn)
    for idx,(chunk_start,chunk_end) in enumerate(chunks):
        chunk_fn = output_dir + fn.replace('/', '_') + 'chunk_' + str(idx) + '.partial'
        curl_args = ['curl', '--progress-bar', '--range', str(chunk_start) + '-' +
                     str(chunk_end),  base_url + fn, '--output', chunk_fn]
        res = subprocess.run(curl_args, check=True)
        chunk_fns.append(chunk_fn)
    catted = output_dir + fn
    os.makedirs(os.path.dirname(output_dir + fn), exist_ok=True)
    cat_args = ['cat']
    cat_args.extend(chunk_fns)
    catted_fd = open(catted, 'w')
    subprocess.run(cat_args, check=True, stdout=catted_fd)
    catted_fd.flush()
    catted_fd.close()
    [os.remove(c) for c in chunk_fns]
    # verify the md5 of the catted file
    if md5:
        md5_args = ['md5sum', catted]
        res = subprocess.run(md5_args, check=True, stdout=subprocess.PIPE)
        computed_md5 = str(res.stdout, 'utf-8').split(' ')[0]
        if computed_md5 != md5:
            print('ERROR! md5 does not match for fn ' + catted)
        else:
            print('SUCCESS! md5 matches for fn ' + catted)
        
        
        
        
        
        
        
