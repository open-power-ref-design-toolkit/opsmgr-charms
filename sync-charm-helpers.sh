#!/bin/bash
set -e
set -o pipefail

script_path=$(dirname "$0")
$script_path/make_all.sh sync-charm-helpers
