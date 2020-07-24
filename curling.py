# Python 3.6.9 (module anaconda3-2019b)
import sys
import subprocess
import math
import os
import hashlib

chunk_size_gb=9.5
output_dir = sys.argv[1].strip()
base_url = sys.argv[2].strip()
if base_url[-1] != '/':
    base_url += '/'
# list of files with format: [<MD5> |sha256:<sha256> ]<relative file path>
# the hash is optional
file_list = sys.argv[3]
files = {} # {file_name -> (size, hash_code, hash_type)}
file_list_fd = open(file_list, 'r')
for line in file_list_fd:
    spl = line.split(' ')
    hash_type = 'md5'
    if len(spl) == 2:
        hash_code = spl[0]
        if len(hash_code.split(':')) == 2:
            s = hash_code.split(':')
            hash_code = s[1]
            hash_type = s[0]            
        fn = spl[1].strip()
    elif len(spl) == 1:
        hash_code = None
        fn = spl[0].strip()
    else:
        assert False # bad format
    # user curl to figure out the size (in bytes) of the file
    curl_args = ['curl', '-sI', base_url + fn]
    print(' '.join(curl_args))
    header = subprocess.run(curl_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    nbytes = -1
    for entry in str(header.stdout, 'utf-8').split('\r\n'):
        spl = entry.split(':')
        if spl[0] == 'Content-Length':
            nbytes = int(spl[1].strip())
            break
    assert nbytes >= 0
    print(nbytes)
    files[fn] = (nbytes, hash_code, hash_type)
file_list_fd.close()

# now split up the files into chunks (10GB is the upper limit that can cause issues)
file_chunks = {} # {file_name -> [list of chunk ranges]}
max_bytes = math.floor(chunk_size_gb * 1024 * 1024 * 1024)
for fn,(sz,a,b) in files.items():
    print(fn)
    chunks = []
    for b in range(0, sz, max_bytes):
        lower = b
        upper = min(lower+max_bytes-1, sz)
        chunks.append((lower, upper))
    file_chunks[fn] = chunks
print(file_chunks)    

# download the chunks and reassemble
for fn,chunks in file_chunks.items():
    hash_code = files[fn][1]
    hash_type = files[fn][2]
    chunk_fns = []
    subprocs = []
    for idx,(chunk_start,chunk_end) in enumerate(chunks):
        chunk_fn = output_dir + fn + '.chunk_' + str(idx) + '.partial'
        curl_args = ['curl', '--range', str(chunk_start) + '-' +
                     str(chunk_end),  base_url + fn, '--output', chunk_fn]
        print('Starting: ' + ' '.join(curl_args))
        res = subprocess.Popen(curl_args)
        subprocs.append((res, ' '.join(curl_args)))
        chunk_fns.append(chunk_fn)
    for sub,args in subprocs:        
        print('Waiting on: ' + args)
        ret = sub.wait()
        assert ret == 0            
    catted = output_dir + fn
    os.makedirs(os.path.dirname(output_dir + fn), exist_ok=True)
    cat_args = ['cat']
    cat_args.extend(chunk_fns)
    catted_fd = open(catted, 'w')
    subprocess.run(cat_args, check=True, stdout=catted_fd)
    catted_fd.flush()
    catted_fd.close()
    [os.remove(c) for c in chunk_fns]
    # verify the hash_code of the catted file
    if hash_code:
        if hash_type.lower() == 'md5':            
            hash_code_args = ['md5sum', catted]
        elif hash_type.lower() == 'sha256':
            hash_code_args = ['sha256sum', catted]
        else:
            assert False
        res = subprocess.run(hash_code_args, check=True, stdout=subprocess.PIPE)
        computed_hash_code = str(res.stdout, 'utf-8').split(' ')[0]
        if computed_hash_code != hash_code:
            print('ERROR! hash code does not match for fn ' + catted)
            assert False
        else:
            print('SUCCESS! hash code matches for fn ' + catted)
        
        
        
        
        
        
        
