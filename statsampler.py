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

unknown = dict()
with io.open('families.md5', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		file = line[34:].rstrip()
		if hash not in dates:
			if file not in unknown:
				unknown[file] = []
			unknown[file].append(hash)

INFINITY = 1e9
score = dict()
total_stdev = 0
for file in unknown.keys():
	stdev = stats[file]['stdev']
	if stdev > INFINITY:
		stdev = INFINITY
	score[file] = stdev * len(unknown[file])
	total_stdev += score[file]

with io.open('todo.md5', 'wb') as todo:
	count = int(sys.argv[1])
	for file in sorted(unknown.keys(), key=lambda file: -score[file]):
		# ceil() so we have a chance to spot files where the known samples
		# suggest a really low stdev, but the file itself actually has a high
		# stdev nevertheless.
		n = min(int(ceil(count * score[file] / total_stdev)), len(unknown[file]))
		for i in range(n):
			index = random.randrange(len(unknown[file]))
			hash = unknown[file].pop(index)
			todo.write(hash + '  ' + file + '\n')
		if n > 0:
			print file, n, score[file]
