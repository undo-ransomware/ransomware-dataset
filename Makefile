all: dates.json popular-ransomware.pdf

ransomware/%.jsons.gz: filter1.py families.md Raw/%.ldjson.tar.gz \
		vxshare-filetypes/%.zip.file.json.gz
	python filter1.py $*

ransomware.jsons: $(foreach id,$(wildcard Raw/*.ldjson.tar.gz), \
		$(subst .ldjson.tar.gz,.jsons.gz,$(subst Raw/,ransomware/,$(id))))
	python filter1combine.py >ransomware.jsons

ransomware.labels: ransomware.jsons avclass/avclass_labeler.py
	python avclass/avclass_labeler.py -vt ransomware.jsons >$@

ransomware.md5: ransomware.labels ransomware.jsons
	python filter2.py ransomware

popular-ransomware.pdf ransomware-family-distribution.pdf: ransomware.labels \
		barplot.py
	python barplot.py

# deliberately using the MetaInfo directory itself as prerequisite. declaring
# all files takes almost 1min just for make to list the files. directory mtime
# changes whenever a file is added, and files are never modified anyway.
sampledates.json: ransomware.md5 sampledates.py MetaInfo/
	python sampledates.py

filedates.pdf filedates.json: sampledates.json ransomware.md5 filedates.py \
		filedates.r
	python filedates.py

dates.json familydates.pdf: sampledates.json filedates.json ransomware.md5 \
		dates.py familydates.r
	python dates.py

todo.md5: sampledates.json sampledates.json filedates.json ransomware.md5 \
		statsampler.py
	python statsampler.py 1440

# these files take about 1 hour to build. ransomware.jsons is about 3.5GB.
# .PRECIOUS makes sure make doesn't accidentally delete any of them.
.PRECIOUS: ransomware/*.jsons.gz ransomware.jsons ransomware.labels \
	families.md5 ransomware.md5
