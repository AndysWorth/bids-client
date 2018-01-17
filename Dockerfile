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

RUN apk add --no-cache nodejs build-base

# Install jsonschema
RUN pip install jsonschema==2.6.0 flywheel-sdk>=2.1.1

ENV SRCDIR /src
RUN mkdir -p ${SRCDIR}
RUN wget -O - https://github.com/INCF/bids-validator/archive/0.25.14.tar.gz | tar xz -C ${SRCDIR}
RUN npm install -g /src/bids-validator-0.25.14/

# Copy code into place
ENV ROOTDIR /code
RUN mkdir -p ${ROOTDIR}
COPY supporting_files ${ROOTDIR}/supporting_files
COPY upload_bids.py ${ROOTDIR}/upload_bids.py
COPY export_bids.py ${ROOTDIR}/export_bids.py
COPY curate_bids.py ${ROOTDIR}/curate_bids.py
COPY templates ${ROOTDIR}/templates

