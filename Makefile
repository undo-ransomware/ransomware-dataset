all: dates.json ransomware-families.pdf

ransomware/%.jsons.gz: filter1.py families.md Raw/%.ldjson.tar.gz \
		vxshare-filetypes/%.zip.file.json.gz
	python filter1.py $*

ransomware.jsons: $(foreach id,$(wildcard Raw/*.ldjson.tar.gz), \
		$(subst .ldjson.tar.gz,.jsons.gz,$(subst Raw/,ransomware/,$(id))))
	python filter1combine.py >ransomware.jsons

ransomware.labels: ransomware.jsons avclass/avclass_labeler.py
	python avclass/avclass_labeler.py -vt ransomware.jsons >$@

samples.json: filter2.py ransomware.labels ransomware.jsons
	python filter2.py

ransomware-families.pdf: samples.json barplot.py
	python barplot.py

# deliberately using the MetaInfo directory itself as prerequisite. declaring
# all files takes almost 1min just for make to list the files. directory mtime
# changes whenever a file is added, and files are never modified anyway.
sampledates.json: samples.json sampledates.py MetaInfo/
	python sampledates.py

filedates.pdf filedates.json: sampledates.json samples.json filedates.py \
		filedates.r
	python filedates.py

dates.json: sampledates.json filedates.json samples.json dates.py
	python dates.py

todo.md5: sampledates.json filedates.json samples.json statsampler.py
	python statsampler.py 1440

# these files take about 1 hour to build. ransomware.jsons is around 1.1GB.
# .PRECIOUS makes sure make doesn't accidentally delete any of them.
.PRECIOUS: ransomware/*.jsons.gz ransomware.jsons ransomware.labels \
	families.md5 ransomware.md5
