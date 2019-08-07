# coding=utf-8
import ast
import os
import io
import json
import sys
import re
from datetime import date

if not os.path.isfile('index.md5'):
	sys.stderr.write('index missing! generate index.md5 by doing:\n')
	sys.stderr.write('  find /path/to/samples -type f -print0 | xargs -0 md5sum >index.md5\n')
	sys.exit(1)

available = dict()
with io.open('index.md5', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		path = line[34:].rstrip()
		available[hash] = path
with io.open('sha256.json', 'rb') as cache:
	sha256 = json.load(cache)

def scan(infile, selected):
	for line in infile:
		selected.append(line[0:32])

selected = []
if len(sys.argv) > 1:
	for file in sys.argv[1:]:
		if os.path.isfile(file):
			with io.open(file, 'rb') as infile:
				scan(infile, selected)
		elif re.match('[0-9a-f]{32}$', file):
			selected.append(file)
		else:
			raise Exception(file + ' is neither a hash nor a file')
else:
	scan(sys.stdin, selected)

for hash in selected:
	if hash in available:
		print hash, available[hash]
	else:
		print hash, 'https://virusshare.com/download.4n6?sample=%s' % (sha256[hash])
