# coding=utf-8
import ast
import os
import io
import json
import sys
import re
from numpy import median
from datetime import date

with io.open('samples.json', 'rb') as cache:
	ransomware = json.load(cache)
with io.open('sampledates.json', 'rb') as cache:
	for hash, ts in json.load(cache).items():
		ransomware[hash]['exactdate'] = ts
with io.open('dates.json', 'rb') as cache:
	for hash, ts in json.load(cache).items():
		ransomware[hash]['date'] = ts

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

families = dict()
for hash, data in ransomware.items():
	for family in data['families']:
		if family not in families:
			families[family] = []
		families[family].append(hash)
	
def score(family):
	med = median([ransomware[hash]['date'] for hash in families[family]])
	return lambda hash: (
			hash in available, # prefer samples that we already have
			-len(ransomware[hash]['families']), # prefer isotopically pure samples
			'exactdate' in ransomware[hash], # prefer samples with known date
			-abs(med - ransomware[hash]['date']), # prefer samples near median date
			hash) # deterministically random tiebreaker

def dateinfo(hash):
	ts = ransomware[hash]['date']
	if 'exactdate' in ransomware[hash] and ransomware[hash]['exactdate'] is not None:
		ts = ransomware[hash]['exactdate']
	dt = str(date.fromtimestamp(ts))
	if 'exactdate' not in ransomware[hash]:
		return '~' + dt
	return dt

num = 10
if len(sys.argv) > 1:
	num = int(sys.argv[1])

for family, samples in sorted(families.items()):
	hashes = sorted(samples, key=score(family), reverse=True)
	print '#', family
	for hash in hashes[0:num]:
		path = ' `' + available[hash] + '`' if hash in available else ''
		fams = ' '.join(ransomware[hash]['families'])
		print '- `%s`: %s %s%s' % (hash, dateinfo(hash), fams, path)
