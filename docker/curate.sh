#!/bin/bash
docker build -t flywheel/bids-client .
docker run -it --rm --net docker_back --link=docker_nginx_1 flywheel/bids-client \
	python code/curate_bids.py "$@"

