import ast
import os
import io
import json
import sys
from datetime import date
from numpy import mean

with io.open('sampledates.json', 'rb') as exact:
	dates = json.load(exact)
with io.open('filedates.json', 'rb') as stats:
	filedates = json.load(stats)

total_stdev = 0
with io.open('ransomware.md5', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		file = line[34:].rstrip()
		if hash not in dates or dates[hash] is None:
			dates[hash] = filedates[file]['mean']
			total_stdev += filedates[file]['stdev']

with io.open('dates.json', 'wb') as outfile:
	json.dump(dates, outfile)
print 'total stdev', total_stdev / 86400 / 365, 'years'

samples = dict()
with io.open('ransomware.labels', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		family = line[33:].rstrip()
		if not family.startswith('SINGLETON:'):
			if family not in samples:
				samples[family] = []
			samples[family].append(hash)
print len(samples), 'families'

families = sorted(samples.keys(), key=lambda family: mean([dates[hash] for hash in samples[family]]))
with io.open('familydates.tmp', 'wb') as dataset:
	dataset.write('rank,family,date\n')
	rank = 0
	for family in families:
		for hash in samples[family]:
			if len(samples[family]) > 3:
				dataset.write(str(rank) + ',' + family + ',' + str(date.fromtimestamp(dates[hash])) + '\n')
		rank += 1
os.system('R --vanilla --slave -f familydates.r')
os.remove('familydates.tmp')
