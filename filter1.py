import os
import io
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

def clone(data, *keys):
	return { key: data[key] for key in keys }

def filter(file, infile, outfile):
	# pre-filter for PE executables. mostly meant to remove browser-based
	# HTML ransom notices, which don't affect files (in a working browser).
	peexe = set()
	with gzip.open(TYPES + file + '.zip.file.json.gz', 'rb') as types:
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

	lineno = 0
	for line in infile:
		if '\x00' in line:
			break
		# filter before parsing to avoid unnexessary parsing
		if 'ransom' in line.lower():
			data = json.loads(line)
			if data['md5'] in peexe:
				obj = clone(data, 'md5', 'sha1', 'sha256')
				obj['file'] = file
				obj['line'] = lineno
				# deliberately using the verbose format that avclass can read
				obj['scans'] = { engine: clone(res, 'detected', 'result')
						for engine, res in data['scans'].items() if res['detected'] }
				obj['undetected'] = [engine
						for engine, res in data['scans'].items() if not res['detected']]
				json.dump(obj, outfile)
				outfile.write('\n')
		lineno += 1
	return lineno

lens = dict()
with io.open('ransomware.jsons', 'wb') as ransom:
	for file in sorted(os.listdir(RAW)):
		if not file.endswith('.ldjson.tar.gz'):
			print file, '???'
			continue
		with gzip.open(RAW + file, 'rb') as tgz:
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
			basename = file[:-14]
			lens[basename] = filter(basename, tgz, ransom)
			print basename, lens[basename]
with io.open('filelengths.json', 'wb') as lengths:
	json.dump(lens, lengths)
