#!/bin/bash

mdb_dir="$1"
csv_dir="$2"

if [ -z "$mdb_dir" -o -z "$csv_dir" ] ; then
  echo "Usage: mdb2csv.bash <mbd_dir> <csv_dir>"
  exit
fi

for lang in 'Ayta_Mag-indi' 'English' 'Ibwe' 'Ingush' 'Migabac' 'Russian' 'Tagalog' ; do
  echo $lang
  mkdir -p $csv_dir/$lang
  for table in $(mdb-tables $mdb_dir/${lang}.mdb) ; do
    echo "  $table"
    mdb-export $mdb_dir/${lang}.mdb $table > $csv_dir/$lang/$(basename $table .mdb).csv
  done
done

