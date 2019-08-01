import os
import io
import re
import sys
import gzip
import json

# directory containing (compressed) downloaded files from
# https://drive.google.com/drive/folders/1oKr5hP8Dlz1QABUOX-HKi2n8tyRkbaDN
# that's 19GB compressed / 200GB uncompressed; this script runs about 30min.
RAW = 'Raw/'
# directory containing the VirusShare_*.zip.file.json files from
# https://a4lg.com/downloads/vxshare/
# they're in the vxshare-filetypes-???-v5.tar.xz files.
# these are gzip compressed to save storage.
# processing time 3-4min, dominated by JSON parsing.
TYPES = 'vxshare-filetypes/'

def match(data, family_filters):
	return [family for family, words in family_filters.items()
			if all(word in data for word in words)]

def scan_jsons(basename, family_filters):
	peexe = set()
	with gzip.open(TYPES + basename + '.zip.file.json.gz', 'rb') as types:
		for row in json.load(types):
			if 'sig' not in row:
				# there's a few (1260) entries missing the "file" results.
				# they're all ELF's, so it doesn't matter.
				continue
			if row['sig'].startswith('PE'):
				f = row['f']
				if not f.startswith("VirusShare_"):
					raise Exception('invalid sample name ' + f)
				peexe.add(f[11:].rstrip())

	with gzip.open(RAW + basename + '.ldjson.tar.gz', 'rb') as tgz:
		# the Raw dataset files are single-element tar.gz files, which is a bit
		# silly. however, since all tars are single-element, so we can just strip
		# a single 512-byte tar header block and treat the rest of the file as
		# ordinary text.
		# since the files always end with a newline, tar's zero-padding of the
		# last block appears as a line containing only NUL bytes, which won't
		# match the "ransom" filter anyway.
		tar_header = tgz.read(512)
		if len(tar_header) != 512:
			raise Exception('cannot skip the TAR header?')
		for line in tgz:
			if '\x00' in line:
				break
			line = line.lower()
			# pre filter before parsing to avoid unnexessary parsing
			if 'ransom' not in line and len(match(line, family_filters)) == 0:
				continue
			data = json.loads(line)
			# pre-filter for PE executables. mostly meant to remove
			# browser-based HTML ransom notices, which cannot affect files
			# (in a working browser).
			if data['md5'] not in peexe:
				continue
			yield data

family_filters = dict()
with io.open('families.md', 'rb') as families:
	for line in families: # find the first table
		if line.startswith('|---'):
			break
	for line in families:
		if not line.startswith('|'):
			break
		family = line.split(r'|')[1].strip()
		if '~~' not in family:
			family_filters[family] = re.split('[ ./-]+', family.lower())

if len(sys.argv) < 2:
	sys.stderr.write('usage: python filter1.py basename\n')
	sys.exit(1)
basename = sys.argv[1]

with gzip.open('ransomware/' + basename + '.tmp', 'wb') as ransomware:
	# stream over the actual metadata files. they're too large to hold in
	# memory.
	for data in scan_jsons(basename, family_filters):
		ransom = False
		detections = dict()
		families = set()
		undetected = []
		for engine, res in data['scans'].items():
			if res['detected']:
				result = res['result']
				detections[engine] = result
				families.update(match(result, family_filters))
				ransom |= 'ransom' in result
			else:
				undetected.append(engine)
		if not ransom or len(families) == 0:
			# prefilter detected keywords that are in the same line, but
			# not in the same engine's detection
			continue

		obj = { key: data[key] for key in ['md5', 'sha1', 'sha256'] }
		obj['file'] = basename
		# deliberately using the verbose format that avclass can read
		obj['scans'] = { engine: { 'detected': True, 'result': res }
				for engine, res in detections.items() }
		obj['undetected'] = undetected
		obj['families'] = list(families)
		json.dump(obj, ransomware)
		ransomware.write('\n')
os.rename('ransomware/' + basename + '.tmp', 'ransomware/' + basename + '.jsons.gz')
