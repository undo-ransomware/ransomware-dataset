## statistics-aware sampler for metadata download ##
# the metadata samples are chosen preferentially from files with high 
# stdev. these give the lowest overall error when the submission date of
# samples is estimated from their file's average submission time.
import io
import sys
import json
import random
from math import ceil
from datetime import date

with io.open('sampledates.json', 'rb') as cache:
	dates = json.load(cache)
with io.open('filedates.json', 'rb') as cache:
	stats = json.load(cache)
with io.open('samples.json', 'rb') as infile:
	ransomware = json.load(infile)

def append(groups, group, item, stdev):
	if group not in groups:
		groups[group] = { 'stdev': 0, 'items': [] }
	groups[group]['items'].append(item)
	groups[group]['stdev'] += stdev

INFINITY = 1e9
families = dict()
labeled = dict()
for hash, data in ransomware.items():
	if hash in dates:
		continue
	file = data['file']
	stdev = stats[file]['stdev']
	if stdev > INFINITY:
		stdev = INFINITY
	if len(data['families']) > 0:
		for family in data['families']:
			append(families, family, hash, stdev)
	else:
		append(labeled, file, hash, stdev)

def sample(grouped, count, todo):
	total_score = sum(data['stdev'] for data in grouped.values())
	for group in sorted(grouped, key=lambda group: -grouped[group]['stdev']):
		# ceil() so we have a chance to spot files where the known samples
		# suggest a really low stdev, but the file itself actually has a high
		# stdev nevertheless.
		unknown = grouped[group]['items']
		score = grouped[group]['stdev']
		n = min(int(ceil(count * score / total_score)), len(unknown))
		for i in range(n):
			index = random.randrange(len(unknown))
			hash = unknown.pop(index)
			todo.write(hash + '  ' + group + '\n')
		if n > 0:
			print group, n, score

with io.open('todo.md5', 'wb') as todo:
	count = int(sys.argv[1])
	sample(families, count, todo)
	sample(labeled, count, todo)
