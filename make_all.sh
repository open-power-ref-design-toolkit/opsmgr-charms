#!/bin/bash
set -e
set -o pipefail

script_path=$(dirname "$0")

for dir in `find $script_path -type f -name 'Makefile' -printf '%h\n'`
do
    echo Running make against: $dir
    make -C $dir $1
done

