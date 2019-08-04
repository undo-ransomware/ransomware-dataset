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

with io.open('samples.json', 'rb') as infile:
	ransomware = json.load(infile)
index = 0
for hash, data in ransomware.items():
	if hash not in dates:
		metafile ='MetaInfo/' + hash + '.json'
		if os.path.isfile(metafile):
			with open(metafile, 'r') as meta:
				try:
					data = ast.literal_eval(meta.readline())
				except Exception:
					print 'crash parsing', hash
					raise
				attrs = data['data']['attributes']
				if 'first_submission_date' in attrs:
					dates[hash] = int(attrs['first_submission_date'])
				else:
					dates[hash] = None

	index += 1
	if index % 1000 == 0:
		sys.stderr.write('\r%dk  ' % (index / 1000))
		sys.stderr.flush()
sys.stderr.write('\r%d / %d  \n' % (len(dates), index))

with io.open('sampledates.json', 'wb') as outfile:
	json.dump(dates, outfile)
