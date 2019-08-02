import os
import io
import json
import sys

# ignore all SINGLETON samples. these are the ones for which not a single AV
# engine has a non-generic name. rationale is that if it isn't important
# enough to get a name, it never had any significant spread.
labels = dict()
with io.open('ransomware.labels', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		label = line[33:].rstrip()
		if not label.startswith('SINGLETON:'):
			labels[hash] = label
sys.stderr.write(str(len(labels)) + ' non-singleton samples\n')

# ransomware.md5 just lists the hashes, and sample source files. because it is
# much smaller, processing it is orders of magnitude faster.
meta = dict()
with io.open('ransomware.jsons', 'rb') as ransom:
	index = 0
	selected = 0
	for line in ransom:
		data = json.loads(line)
		hash = data['md5']
		families = data['families']
		if hash in labels or len(families) > 0:
			obj = { key: data[key] for key in ['families', 'file'] }
			obj['label'] = labels[hash] if hash in labels else None
			meta[hash] = obj
			selected += 1

		index += 1
		if index % 1000 == 0:
			sys.stderr.write('\r' + str(index / 1000) + 'k  ')
			sys.stderr.flush()
sys.stderr.write('\r' + str(selected) + ' / ' + str(index) + '\n')

with io.open('samples.json', 'wb') as out:
	json.dump(meta, out)
