import ast
import os
import io
import json
import sys

if os.path.isfile('sampledates.json'):
	with io.open('sampledates.json', 'rb') as cache:
		dates = json.load(cache)
else:
	dates = dict()

index = 0
with io.open('ransomware.md5', 'rb') as infile:
	for line in infile:
		hash = line[0:32]
		if hash not in dates:
			metafile ='MetaInfo/' + hash + '.json'
			if os.path.isfile(metafile):
				with open(metafile, 'r') as meta:
					data = ast.literal_eval(meta.readline())
					attrs = data['data']['attributes']
					if 'first_submission_date' in attrs:
						dates[hash] = int(attrs['first_submission_date'])
					else:
						dates[hash] = None
	
		index += 1
		if index % 1000 == 0:
			sys.stderr.write('\r' + str(index / 1000) + 'k  ')
			sys.stderr.flush()
sys.stderr.write('\r' + str(index) + '\n')

with io.open('sampledates.json', 'wb') as outfile:
	outfile.write(json.dumps(dates))
