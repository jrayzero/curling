# run a sanity check on the hashes (runs in parallel for all files)
import sys
import subprocess

output_dir = sys.argv[1].strip()
file_list = sys.argv[2]

threads = []

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
    catted = output_dir + fn
    if hash_code:
        if hash_type.lower() == 'md5':            
            hash_code_args = ['md5sum', catted]
        elif hash_type.lower() == 'sha256':
            hash_code_args = ['sha256sum', catted]
        else:
            assert False        
        print('Starting: ' + ' '.join(hash_code_args))
        res = subprocess.Popen(hash_code_args, stdout=subprocess.PIPE)
        threads.append((res, ' '.join(hash_code_args), hash_code, fn))
        
for thread,args,hash_code,fn in threads:
    print('waiting on: ' + args)
    computed_hash_code = str(thread.communicate()[0], 'utf-8').split(' ')[0]
    print(computed_hash_code)
    if computed_hash_code != hash_code:
        print('ERROR! hash code does not match for fn ' + fn)
        assert False
    else:
        print('SUCCESS! hash code matches for fn ' + fn)
    

file_list_fd.close()
