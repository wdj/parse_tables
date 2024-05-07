#!/bin/bash

mdb_dir="$1"
csv_dir="$2"

if [ -z "$mdb_dir" -o -z "$csv_dir" ] ; then
  echo "Usage: mdb2csv.bash <mbd_dir> <csv_dir>"
  exit
fi

for db in 'Ayta_Mag-indi' 'English' 'Ibwe' 'Ingush' 'Migabac' 'Russian' 'Tagalog' 'Ontology' ; do
  echo $db
  mkdir -p $csv_dir/$db
  for table in $(mdb-tables $mdb_dir/${db}.mdb) ; do
    echo "  $table"
    mdb-export $mdb_dir/${db}.mdb $table > $csv_dir/$db/$(basename $table .mdb).csv
  done
done

