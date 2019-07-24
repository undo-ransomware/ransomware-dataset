import ast
import os
import io
import json
import sys

with io.open('sampledates.json', 'rb') as exact:
	dates = json.load(exact)
with io.open('filedates.json', 'rb') as stats:
	filedates = json.load(stats)

total_stdev = 0
with io.open('ransomware.md5', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		file = line[34:].rstrip()
		if hash not in dates:
			dates[hash] = filedates[file]['mean']
			total_stdev += filedates[file]['stdev']

with io.open('dates.json', 'wb') as outfile:
	json.dump(dates, outfile)
print 'total stdev', total_stdev / 86400 / 365, 'years'
