#!/usr/bin/env sh

set -eu
unset CDPATH
cd "$( dirname "$0" )/../.."

# TODO: export APIKEY

# Define PYTHONPATH
PYTHONPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH

# Run unit tests
RUN_UNIT=true
if ${RUN_UNIT}; then
    printf "INFO: Running unit tests ...\n"
    pytest tests/test_utils.py
    pytest tests/test_curate_bids.py
    pytest tests/test_export_bids.py
    pytest tests/test_upload_bids.py
    pytest tests/test_bidsify_flywheel.py
fi

