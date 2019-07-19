import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

singletons = 0
counts = {}
with open('ransomware.labels', 'r') as labels:
	# read labels and build counts dict
	for line in labels:
		family = line.strip().split('\t')[1]
		if not family.startswith('SINGLETON:'):
			if family in counts:
				counts[family] += 1
			else:
				counts[family] = 1
		else:
			singletons += 1
print 'Ignoring', singletons, 'SINGLETON detections'

single = 0
for family in counts.keys():
	if counts[family] == 1:
		single += 1
		del counts[family]
print 'Ignoring', single, 'families with only one sample'
print 'Number of families: ' + str(len(counts.keys()))

families = sorted(counts.keys(), key=lambda family: -counts[family])

with PdfPages('ransomware-family-distribution.pdf') as pdf:
	plt.figure(figsize=(12, 9))
	plt.ylabel('Number of samples')
	plt.xlabel('Ransomware family (rank)')
	plt.title('Distribution of ransomware families')
	plt.yscale('log')

	bars = []
	height = []
	for family in families:
		bars.append(family)
		height.append(counts[family])

	# this is too dense to actually distinguish individual bars anyway, so let's
	# just fill the entire area. that's way faster anyway.
	x_pos = np.arange(len(bars))
	plt.fill_between(x_pos, 0, height)
	pdf.savefig()
	plt.close()

with PdfPages('popular-ransomware.pdf') as pdf:
	plt.figure(figsize=(12, 9))
	plt.ylabel('Number of samples')
	plt.xlabel('Ransomware family')
	plt.title('Most popular ransomware families')
	plt.yscale('log')

	bars = []
	height = []
	for family in families:
		if counts[family] > 1000:
			bars.append(family)
			height.append(counts[family])

	# this is too dense to actually distinguish individual bars anyway, so let's
	# just fill the entire area. that's way faster anyway.
	x_pos = np.arange(len(bars))
	pbars = plt.bar(x_pos, height, 0.8)
	 
	# create names on the x-axis
	plt.xticks(x_pos, bars, rotation=-90)

	for rect in pbars:
		height = rect.get_height()
		plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom', rotation=-90, size=8)
	 
	plt.subplots_adjust(bottom=0.15)
	pdf.savefig()
	plt.close()
