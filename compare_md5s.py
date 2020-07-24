import sys

md5list_0 = sys.argv[1]
md5list_1 = sys.argv[2]
output = sys.argv[3]
ofd = open(output, 'w')
md5s = {}
fd = open(md5list_0, 'r')
for md5 in fd:
    md5 = md5.split(' ')
    md5s[md5[1]] = md5[0]
fd.close()
fd = open(md5list_1, 'r')
for md5 in fd:
    md5 = md5.split(' ')
    fn = md5[1]
    md5 = md5[0]
    if md5 != md5s[fn]:
        ofd.write(fn)
ofd.flush()
ofd.close()
fd.close()
    
