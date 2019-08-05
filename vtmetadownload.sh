#!/bin/bash -e
if [ -z "$1" ]; then
	echo "usage:   $0 file.md5..."
	echo "usually: while sleep 1; do make todo.md5 && $0 todo.md5; done"
	exit 1
fi
METAINFO=/home/matthias/ransomware/MetaInfo
cat "$@" | while read hash _; do
	if ! [ -s $METAINFO/$hash.json ]; then
		echo $hash
		python /home/matthias/ransomware/VirusTotalApi/vt/vt.py -s -j --allinfo $hash >$METAINFO/$hash.json
		sleep 10
	fi
	mv VTDL_*.json vtdl
done
