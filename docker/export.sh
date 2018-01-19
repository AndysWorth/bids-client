#!/bin/bash
if [ -d "$1" ]; then
	BIDS_DIR=`realpath $1`
	echo "Using bids dir: ${BIDS_DIR}"
	shift
else
	echo "Usage: $0 <bids-dir> [options...]"
	exit 1
fi

docker build -t flywheel/bids-client .
docker run -it --rm --net docker_back --link=docker_nginx_1 \
	-v ${BIDS_DIR}:/local/bids \
	flywheel/bids-client \
	python code/export_bids.py --bids-dir /local/bids "$@"

