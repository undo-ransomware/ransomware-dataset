import os
import io
import json
import sys

# ignore all SINGLETON samples. these are the ones for which not a single AV
# engine has a non-generic name. rationale is that if it isn't important
# enough to get a name, it never had any significant spread.
recognized = dict()
with io.open('ransomware.labels', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		family = line[33:].rstrip()
		if not family.startswith('SINGLETON:'):
			recognized[hash] = family
sys.stderr.write(str(len(recognized)) + ' non-singleton samples\n')

stats = dict()
with io.open('ransomware.jsons', 'rb') as ransom:
	total = 0
	for line in ransom:
		data = json.loads(line)
		hash = data['md5']
		file = data['file']
		for family in data['families']:
			if family not in stats:
				stats[family] = { 'samples': 0, 'labels': dict(),
						'unicorns': 0, 'detect': 0, 'ransom': 0 }
			stats[family]['samples'] += 1
			if hash in recognized:
				label = recognized[hash]
				if label not in stats[family]['labels']:
					stats[family]['labels'][label] = 0
				stats[family]['labels'][label] += 1
			if len(data['families']) == 1:
				stats[family]['unicorns'] += 1
			stats[family]['detect'] += len(data['scans'])
			stats[family]['ransom'] += sum(1 for eng, res in data['scans'].items()
					if 'ransom' in res['result'].lower())

		total += 1
		if total % 1000 == 0:
			sys.stderr.write('\r' + str(total / 1000) + 'k  ')
			sys.stderr.flush()
sys.stderr.write('\r' + str(total) + '\n')

for family, stat in stats.items():
	samples = stat['samples']
	stat['fraction'] = samples / float(total)
	stat['unicorns'] /= float(samples)
	stat['labels'] = len(stat['labels'])
	stat['ransom'] /= float(stat['detect'])
	stat['score'] = stat['samples'] * stat['labels'] / (stat['ransom'] + 1e-5)
families = sorted(stats.keys(), key=lambda family: stats[family]['score'])

with io.open('genericide.md', 'wb') as select:
	select.write('| %-14s | %-7s | %-6s | %-8s | %-8s | %-8s |\n' % ('family', 'samples', 'labels', 'ransom', 'fraction', 'unicorns'))
	select.write('|-%-14s-|-%-7s-|-%-6s-|-%-8s-|-%-8s-|-%-8s-|\n' % ('-'*14, '-'*7, '-'*6, '-'*8, '-'*8, '-'*8))
	for family in families:
		stat = stats[family]
		select.write('| %-14s | %-7d | %-6d | %8.5f | %8.5f | %8.5f |\n' %
				(family, stat['samples'], stat['labels'], stat['ransom'] * 100, stat['fraction'] * 100, stat['unicorns']))
