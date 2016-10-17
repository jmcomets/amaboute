#!/bin/bash
set -e

db_name=messages.db
tables="messages profiles"
backup_dir=database-backup-`date -I`

mkdir $backup_dir
for t in $tables; do
    sqlite3 $db_name <<< ".dump $t" > $backup_dir/$t.sql
done

backup_file=$backup_dir.tar.gz
tar czf $backup_file $backup_dir/*
rm -rf $backup_dir

echo "Backup: $backup_file"
