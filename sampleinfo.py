# coding=utf-8
import ast
import os
import io
import json
import sys
import re
from datetime import date

with io.open('sampledates.json', 'rb') as cache:
	dates = json.load(cache)
with io.open('filedates.json', 'rb') as cache:
	filedates = json.load(cache)

ransomware = dict()
with io.open('ransomware.md5', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		file = line[34:].rstrip()
		ransomware[hash] = file

fam = dict()
with io.open('ransomware.labels', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		family = line[33:].rstrip()
		fam[hash] = family

def family(hash):
	return fam[hash] if hash in fam else '???'

def dateinfo(hash):
	if hash in dates:
		return str(date.fromtimestamp(dates[hash]))
	stats = filedates[ransomware[hash]]
	stdev = stats['stdev'] / 86400
	return str(date.fromtimestamp(stats['mean'])) + (' ±%.1f' % stdev) + ' days'

def query(hash):
	if hash in ransomware:
		selected.append(hash)

def scan(infile, selected):
	for line in infile:
		hash = line[0:32]
		query(hash)

selected = []
if len(sys.argv) > 1:
	for file in sys.argv[1:]:
		if os.path.isfile(file):
			with io.open(file, 'rb') as infile:
				scan(infile, selected)
		elif re.match('[0-9a-f]{32}$', file):
			query(file)
		else:
			raise Exception(file + ' is neither a hash nor a file')
else:
	scan(sys.stdin, selected)
for hash in sorted(selected, key=family):
	print hash, ransomware[hash], family(hash), dateinfo(hash)
