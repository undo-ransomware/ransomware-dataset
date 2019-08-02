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
with io.open('samples.json', 'rb') as infile:
	ransomware = json.load(infile)

total_stdev = 0
for hash, data in ransomware.items():
	if hash not in dates or dates[hash] is None:
		file = data['file']
		dates[hash] = filedates[file]['mean']
		total_stdev += filedates[file]['stdev']

with io.open('dates.json', 'wb') as outfile:
	json.dump(dates, outfile)
print 'total stdev', total_stdev / 86400 / 365, 'years'
