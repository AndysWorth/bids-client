# bids-uploader
#
# Upload BIDS dataset
#
# Example usage:
# docker run --rm -it \
#    -v  /path/to/bids/directory:/bids_dir \
#    bids-uploader /bin/bash


FROM python:2.7
MAINTAINER Flywheel <support@flywheel.io>

# Install jsonschema
RUN pip install jsonschema==2.6.0

# Install BIDS validator from INCF
#     https://github.com/INCF/bids-validator
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
    apt-get remove -y curl && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV SRCDIR /src
RUN mkdir -p ${SRCDIR}
RUN wget -O - https://github.com/INCF/bids-validator/archive/0.24.0.tar.gz | tar xz -C ${SRCDIR}
RUN npm install -g /src/bids-validator-0.24.0/


# Install python SDK
RUN pip install https://github.com/flywheel-io/sdk/releases/download/0.3.0/flywheel-0.3.0-py2-none-linux_x86_64.whl

# Copy code into place
ENV ROOTDIR /code
RUN mkdir -p ${ROOTDIR}
COPY supporting_files ${ROOTDIR}/supporting_files
COPY upload_bids.py ${ROOTDIR}/upload_bids.py
COPY export_bids.py ${ROOTDIR}/export_bids.py
COPY curate_bids.py ${ROOTDIR}/curate_bids.py
COPY templates ${ROOTDIR}/templates

