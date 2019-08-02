import io
import json
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

with io.open('samples.json', 'rb') as infile:
	ransomware = json.load(infile)

labelcounts = Counter()
familycounts = Counter()
for hash, data in ransomware.items():
	if len(data['families']) > 0:
		for family in data['families']:
			familycounts[family] += 1
	else:
		labelcounts[data['label']] += 1

single = 0
for family in labelcounts.keys():
	if labelcounts[family] == 1:
		single += 1
		del labelcounts[family]
print 'Ignoring', single, 'labels with only one sample'
print 'Number of familis: ' + str(len(familycounts.keys()))
print 'Number of labels: ' + str(len(labelcounts.keys()))

def families(counts):
	return sorted(counts.keys(), key=lambda family: -counts[family])

def render(counts, pdf, cutoff, label):
	plt.figure(figsize=(12, 10))
	plt.ylabel('Number of samples')
	plt.xlabel(label)
	#plt.title('Most popular ransomware families')
	plt.yscale('log')

	bars = []
	height = []
	for family in families(counts):
		if counts[family] > cutoff:
			bars.append(family)
			height.append(counts[family])

	x_pos = np.arange(len(bars))
	pbars = plt.bar(x_pos, height, 0.8)
	 
	# create names on the x-axis
	plt.xticks(x_pos, bars, rotation=-90, size=7)

	for rect in pbars:
		height = rect.get_height()
		plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom', rotation=-90, size=7)
	 
	plt.subplots_adjust(bottom=0.15)
	pdf.savefig()

with PdfPages('ransomware-families.pdf') as pdf:
	render(familycounts, pdf, 0, 'Ransomware families')
	render(labelcounts, pdf, 500, 'AVclass labels')

	plt.figure(figsize=(12, 10))
	plt.ylabel('Number of samples')
	plt.xlabel('AVclass label (rank)')
	plt.title('Distribution of ransomware labels')
	plt.yscale('log')

	bars = []
	height = []
	for family in families(labelcounts):
		bars.append(family)
		height.append(labelcounts[family])

	# this is too dense to actually distinguish individual bars anyway, so let's
	# just fill the entire area. that's way faster anyway.
	x_pos = np.arange(len(bars))
	plt.fill_between(x_pos, 0, height)
	pdf.savefig()

	plt.close()
