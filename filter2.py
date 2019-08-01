import os
import io
import json
import sys

if len(sys.argv) < 2:
	sys.stderr.write('usage: python filter2.py basename\n')
	sys.exit(1)
basename = sys.argv[1]

# ignore all SINGLETON samples. these are the ones for which not a single AV
# engine has a non-generic name. rationale is that if it isn't important
# enough to get a name, it never had any significant spread.
recognized = set()
with io.open(basename + '.labels', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		family = line[33:].rstrip()
		if not family.startswith('SINGLETON:'):
			recognized.add(hash)
sys.stderr.write(str(len(recognized)) + ' non-singleton samples\n')

# ransomware.md5 just lists the hashes, and sample source files. because it is
# much smaller, processing it is orders of magnitude faster.
sourcefile = dict()
with io.open(basename + '.jsons', 'rb') as ransom, io.open(basename + '.md5', 'wb') as md5:
	index = 0
	selected = 0
	for line in ransom:
		data = json.loads(line)
		hash = data['md5']
		file = data['file']
		if hash in recognized:
			md5.write(hash + '  ' + file + '\n')
			selected += 1

		index += 1
		if index % 1000 == 0:
			sys.stderr.write('\r' + str(index / 1000) + 'k  ')
			sys.stderr.flush()
sys.stderr.write('\r' + str(selected) + ' / ' + str(index) + '\n')
