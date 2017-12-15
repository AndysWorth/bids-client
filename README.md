# bids-client
Holding place for BIDS enabled client
REF: https://flywheelio.aha.io/epics/FW-E-39

## Overview
The BIDS Client has three components:

Upload 
Curate 
Export 

Below is more information about each of the components.

##### Build the image
The following command will build the docker image containing all BIDS Client components.

git clone https://github.com/flywheel-io/bids-client
cd bids-client
docker build -t flywheel/bids-client .


## Upload
The upload script (upload_bids.py) takes a BIDS dataset and uploads it into the 

##### Run Docker image locally
Startup container
```
docker run -it --rm \
    -v /path/to/BIDS/dir/locally:/path/to/BIDS/dir/in/container \
     bids-client /bin/bash
```

Run the upload script
```
python /code/upload_bids.py \
    --bids-dir /path/to/BIDS/dir/in/container \
    --api-key '<PLACE YOUR API KEY HERE>' \
    --type 'Flywheel' \
    -g '<PLACE GROUP ID HERE>'
```

## Curate
The BIDS Curation step (curate_bids.py) has been transformed into a gear for better usability.
The git repo for the gear is here: https://github.com/flywheel-apps/curate-bids

## Export
The export script (export_bids.py) takes a curated dataset within Flywheel and exports it to local disk.

Startup container
```
docker run -it --rm \
    -v /path/to/BIDS/dir/locally:/path/to/BIDS/dir/in/container \
     bids-client /bin/bash
```

Run the export script
```
python /code/export_bids.py \
    --bids-dir /path/to/BIDS/dir/in/container \
    --api-key '<PLACE YOUR API KEY HERE>' \
    -p '<PROJECT LABEL TO DOWNLOAD>'
```
