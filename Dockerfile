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
# Install numpy
RUN pip install numpy==1.13.3


# Install BIDS validator from INCF
#     https://github.com/INCF/bids-validator
#RUN npm install -g /src


# Install python SDK
RUN pip install https://github.com/flywheel-io/sdk/releases/download/0.2.0/flywheel-0.2.0-py2-none-linux_x86_64.whl


# Copy code into place
ENV ROOTDIR /code
RUN mkdir -p ${ROOTDIR}
COPY upload_bids.py ${ROOTDIR}/upload_bids.py
COPY supporting_files ${ROOTDIR}/supporting_files
COPY export_bids.py ${ROOTDIR}/export_bids.py


