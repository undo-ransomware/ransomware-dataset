import os
import io
import subprocess

BIN = 'theZoo/malwares/Binaries/'

def find(dir, ext):
	file = [z for z in os.listdir(dir) if z.endswith(ext)]
	if len(file) != 1:
		raise Exception('more than one ' + ext + ' in ' + dir)
	return dir + '/' + file[0]

sources = dict()
for file in os.listdir(BIN):
	zip = find(BIN + file, '.zip')
	with io.open(find(BIN + file, '.pass'), 'rb') as infile:
		pw = infile.readline().rstrip()
	os.mkdir('temp')
	subprocess.call(['unzip', '-P' + pw, zip, '-d', 'temp'])
	os.system('rm -f temp/.DS_Store')
	for line in subprocess.Popen('find temp -type f -print0 | xargs -0 md5sum',
			shell=True, stdout=subprocess.PIPE).stdout:
		hash = line[0:32]
		sample = line[34:].rstrip()
		name = 'samples/' + hash
		if not os.path.isfile(name):
			os.link(sample, name)
			os.chmod(name, 0644)
		if hash not in sources:
			sources[hash] = []
		sources[hash].append(file)
	os.system('rm -rf temp')

with io.open('theZoo.md5', 'wb') as index:
	for hash in sources.keys():
		for file in sources[hash]:
			index.write(hash + '  ' + file + '\n')
