import os
import io
import json
from datetime import date
from math import sqrt

class FileStats:
	def __init__(self):
		self.mean = 0
		self.var = 0
		self.stdev = float('nan')
		self.known = dict()
	
	def add(self, hash, ts):
		self.known[hash] = ts
		# sum-of-squares algorithm works fine with python's bigints
		self.mean += ts
		self.var += ts * ts

	def finalize(self):
		n = len(self.known)
		if n <= 1:
			# (for 1, mean is well-defined and doesn't need division by 1)
			self.var = self.stdev = float('inf')
			return
		self.var = (self.var - self.mean * self.mean // n) // (n - 1)
		self.mean //= n
		self.stdev = sqrt(self.var)

with io.open('sampledates.json', 'rb') as cache:
	dates = json.load(cache)

samples = dict()
for basename in ['ransomware', 'families']:
	with io.open(basename + '.md5', 'rb') as infile:
		for line in infile:
			hash = line[0:32]
			file = line[34:].rstrip()
			if file not in samples:
				samples[file] = FileStats()
			if hash in dates and dates[hash] is not None:
				samples[file].add(hash, dates[hash])
for file in samples.keys():
	samples[file].finalize()

dates = dict()
for file in sorted(samples.keys()):
	dates[file] = { 'mean': samples[file].mean, 'stdev': samples[file].stdev }
with io.open('filedates.json', 'wb') as outfile:
	json.dump(dates, outfile)

with io.open('filedates.tmp', 'wb') as dataset:
	dataset.write('filename,date\n')
	for file in sorted(samples.keys()):
		for hash, d in samples[file].known.items():
			dataset.write(file[11:16] + ',' + str(date.fromtimestamp(d)) + '\n')
os.system('R --vanilla --slave -f filedates.r')
os.remove('filedates.tmp')
