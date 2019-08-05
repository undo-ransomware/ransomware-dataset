# coding=utf-8
import ast
import os
import io
import json
import sys
import re
from numpy import median
from datetime import date
from collections import Counter

with io.open('samples.json', 'rb') as cache:
	ransomware = json.load(cache)
with io.open('sampledates.json', 'rb') as cache:
	for hash, ts in json.load(cache).items():
		ransomware[hash]['exactdate'] = ts
with io.open('dates.json', 'rb') as cache:
	for hash, ts in json.load(cache).items():
		ransomware[hash]['date'] = ts
with io.open('sha256.json', 'rb') as cache:
	for hash, sha256 in json.load(cache).items():
		ransomware[hash]['sha256'] = sha256

available = dict()
if os.path.isfile('index.md5'):
	with io.open('index.md5', 'rb') as infile:
		for line in infile:
			hash = line[0:32]
			path = line[34:].rstrip()
			available[hash] = path
else:
	sys.stderr.write('index missing! generate index.md5 by doing:\n')
	sys.stderr.write('  find /path/to/samples -type f -print0 | xargs -0 md5sum >index.md5\n')

def score(family):
	med = median([ransomware[hash]['date'] for hash in families[family]])
	return lambda hash: (
			hash in available, # prefer samples that we already have
			-len(ransomware[hash]['families']), # prefer isotopically pure samples
			'exactdate' in ransomware[hash], # prefer samples with known date
			-abs(med - ransomware[hash]['date']), # prefer samples near median date
			hash) # deterministically random tiebreaker

if len(sys.argv) > 1:
	num = int(sys.argv[1])
else:
	num = 10
processed = set()
done = Counter()
for file in sys.argv[2:]:
	family_filters = dict()
	with io.open(file, 'rb') as infile:
		for line in infile: # find the first table
			if line.startswith('|---'):
				break
		for line in infile:
			if not line.startswith('|'):
				break

			task, hash, family = line.split('|')[1:4]
			hash = re.search('`([0-9a-f]{32})`', hash).group(1)
			family = family.strip()
			if '#' in task and '~~' not in task:
				done[family] += 1
			processed.add(hash)

families = dict()
for hash, data in ransomware.items():
	for family in data['families']:
		if hash not in processed:
			if family not in families:
				families[family] = []
			families[family].append(hash)

def dateinfo(meta):
	ts = meta['date']
	if 'exactdate' in meta and meta['exactdate'] is not None:
		ts = meta['exactdate']
	dt = str(date.fromtimestamp(ts))
	if 'exactdate' not in meta:
		return '~' + dt
	return dt

with io.open('suggested.md5', 'wb') as todo, io.open('download.md5', 'wb') as dl:
	for family, samples in sorted(families.items()):
		hashes = sorted(samples, key=score(family), reverse=True)
		n = num - done[family]
		if n <= 0:
			continue
		for hash in hashes[0:n]:
			meta = ransomware[hash]
			fams = ' '.join(meta['families'])
			label = ('`' + meta['label'] + '`') if meta['label'] is not None else 'missing'
			print '| TODO     | `%32s` | %-23s | %-17s | %-11s | `drop`     | 600     | TBD       |' % (
					hash, family, label, dateinfo(meta))
			if hash in available:
				todo.write('%s  %s\n' % (hash, available[hash]))
			else:
				dl.write('%s  https://virusshare.com/download.4n6?sample=%s\n' % (hash, meta['sha256']))
