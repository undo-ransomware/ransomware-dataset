import ast
import os
import io
import json
import sys
from datetime import date
from numpy import median

with io.open('dates.json', 'rb') as exact:
	dates = json.load(exact)
with io.open('samples.json', 'rb') as infile:
	ransomware = json.load(infile)

families = dict()
labels = dict()
known = unknown = 0
for hash, data in ransomware.items():
	for family in data['families']:
		if family not in families:
			families[family] = []
		families[family].append(hash)

	if len(data['families']) == 0:
		label = data['label']
		if label not in labels:
			labels[label] = []
		labels[label].append(hash)
		unknown += 1
	else:
		known += 1

print len(families), 'families containing', known, 'samples'
print len(labels), 'labels for', unknown, 'samples'

med_date = { family: median([dates[hash] for hash in families[family]])
		for family in families.keys() }
fam = sorted(families.keys(), key=lambda family: med_date[family])
with io.open('familydates1.tmp', 'wb') as dataset:
	dataset.write('rank,family\n')
	rank = 1
	for family in fam:
		dataset.write(str(rank) + ',' + family + '\n')
		rank += 1
with io.open('familydates2.tmp', 'wb') as dataset:
	dataset.write('rank,date\n')
	rank = 1
	for family in fam:
		for hash in families[family]:
			dataset.write(str(rank) + ',' + str(date.fromtimestamp(dates[hash])) + '\n')
		rank += 1
os.system('R --vanilla --slave -f familydates.r')
os.remove('familydates1.tmp')
os.remove('familydates2.tmp')
