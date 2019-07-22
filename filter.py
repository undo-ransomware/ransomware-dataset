import os
import io
import gzip
import json

# directory containing (compressed) downloaded files from
# https://drive.google.com/drive/folders/1oKr5hP8Dlz1QABUOX-HKi2n8tyRkbaDN
# that's 19GB compressed / 200GB uncompressed; this script runs about 30min.
DIR = 'Raw/'

def clone(data, *keys):
	return { key: data[key] for key in keys }

def filter(file, infile, outfile, md5file):
	lineno = 0
	for line in infile:
		if '\x00' in line:
			break
		if 'ransom' in line.lower():
			data = json.loads(line)
			obj = clone(data, 'md5', 'sha1', 'sha256')
			obj['scans'] = { engine: clone(res, 'detected', 'result')
					for engine, res in data['scans'].items() if res['detected'] }
			obj['undetected'] = [engine
					for engine, res in data['scans'].items() if not res['detected']]
			obj['file'] = file
			obj['line'] = lineno
			json.dump(obj, outfile)
			outfile.write('\n')
			md5file.write(data['md5'] + '  ' + file + '\n')
		lineno += 1
	return lineno

lens = dict()
with io.open('ransomware.jsons', 'wb') as ransom, io.open('ransomware.md5', 'wb') as md5:
	for file in sorted(os.listdir(DIR)):
		with gzip.open(DIR + file, 'rb') as tgz:
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
			lens[file] = filter(file, tgz, ransom, md5)
			print file, lens[file]
with io.open('filelengths.json', 'wb') as lengths:
	json.dump(lens, lengths)
