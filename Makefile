all: dates.json popular-ransomware.pdf

ransomware.jsons filelengths.json: filter1.py Raw/ vxshare-filetypes/
	python filter1.py

ransomware.labels: ransomware.jsons avclass/avclass_labeler.py
	python avclass/avclass_labeler.py -vt ransomware.jsons >$@

ransomware.md5: ransomware.labels ransomware.jsons
	python filter2.py

popular-ransomware.pdf ransomware-family-distribution.pdf: ransomware.labels \
		barplot.py
	python barplot.py

# deliberately using the MetaInfo directory itself as prerequisite. declaring
# all files takes almost 1min just for make to list the files. directory mtime
# changes whenever a file is added, and files are never modified anyway.
sampledates.json: ransomware.md5 sampledates.py MetaInfo/
	python sampledates.py

filedates.pdf filedates.json: sampledates.json ransomware.md5 filedates.py
	python filedates.py

dates.json: sampledates.json filedates.json ransomware.md5 merge.py
	python merge.py

todo.md5: sampledates.json sampledates.json filedates.json ransomware.md5 \
		statsampler.py
	python statsampler.py 1440

# together, these files take ~35min to build. ransomware.jsons is about 1.0GB.
# .PRECIOUS makes sure make doesn't accidentally delete them.
.PRECIOUS: ransomware.jsons filelengths.json ransomware.labels ransomware.md5
