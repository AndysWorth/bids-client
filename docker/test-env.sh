#!/bin/bash

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

docker run -it --rm \
	-w /local \
	-v $PROJECT_DIR:/local \
	-e PYTHONPATH=/local \
	python:2.7 /bin/bash -c "pip install -r requirements.txt; /bin/bash"

