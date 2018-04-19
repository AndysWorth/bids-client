# bids-uploader
#
# Upload BIDS dataset
#
# Example usage:
# docker run --rm -it \
#    -v  /path/to/bids/directory:/bids_dir \
#    bids-uploader /bin/bash


FROM python:2.7-alpine3.7
MAINTAINER Flywheel <support@flywheel.io>

RUN apk add --no-cache nodejs bash

# Install jsonschema
RUN pip install -qq jsonschema==2.6.0 flywheel-sdk>=2.1.1

ENV SRCDIR /src
RUN mkdir -p ${SRCDIR}
RUN wget -O - https://github.com/INCF/bids-validator/archive/0.25.14.tar.gz | tar xz -C ${SRCDIR}
RUN npm install -g /src/bids-validator-0.25.14/

COPY . /var/flywheel/code/bids-client
RUN pip install --no-deps /var/flywheel/code/bids-client

