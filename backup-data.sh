#!/bin/bash

set -u

archive_filename=data-`date -I`-backup.tar.gz
merged_filename=`python3 merging.py | awk '{print $2}'`
tar cf $archive_filename data/*
rm -f data/*
mv $merged_filename data/$merged_filename
mv $archive_filename backups/$archive_filename
