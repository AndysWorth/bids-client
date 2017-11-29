import argparse
import logging
import os
import re
import sys
import zipfile

import flywheel

from supporting_files import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bids-exporter')

def validate_dirname(dirname):
    """
    Check the following criteria to ensure 'dirname' is valid
        - dirname exists
        - dirname is a directory
    If criteria not met, raise an error
    """
    logger.info('Validating download directory')

    # Check dirname is a directory
    if not os.path.isdir(dirname):
        logger.error('Path (%s) is not a directory' % dirname)
        sys.exit(1)

    # Check dirname exists
    if not os.path.exists(dirname):
        logger.info('Path (%s) does not exist. Making directory...' % dirname)
        os.mkdir(dirname)
    # If directory does exist, make sure it's empty
    else:
        if os.listdir(dirname):
            logger.error('Directory (%s) is not empty. Exporter will not run.' % dirname)
            sys.exit(1)

def validate_project_label(fw, project_label):
    """ """
    # Find project id
    projects = fw.get_all_projects()
    project_found = False
    for p in projects:
        if p['label'] == project_label:
            project_id = p['_id']
            project_found = True

    if not project_found:
        logger.error('Cannot find project %s.' % project_label)
        sys.exit(1)

    return project_id

def define_path(outdir, f, namespace):
    """"""
    # Ensure that the folder exists...
    foldername = os.path.join(outdir,
            f['info'][namespace]['Folder'])
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    # Define path to download file to...
    path = os.path.join(
            foldername,
            f['info'][namespace]['Filename']
        )

    return path

def download_bids_dir(fw, project_id, outdir):
    """

    fw: Flywheel client
    project_label: Label of the project to download
    outdir: path to directory to download files to, string

    """

    # Define namespace
    namespace = 'BIDS'

    # Get project
    project = fw.get_project(project_id)

    logger.info('Downloading project files')
    # Iterate over any project files
    for f in project.get('files', []):
        # Define the folder name
        path = define_path(outdir, f, namespace)
        # Download the file
        fw.download_file_from_project(project['_id'], f['name'], path)
        # If zipfile is attached to project, unzip...
        zip_pattern = re.compile('[a-zA-Z0-9]+(.zip)')
        zip_dirname = path[:-4]
        if zip_pattern.search(path):
            zip_ref = zipfile.ZipFile(path, 'r')
            zip_ref.extractall(zip_dirname)
            zip_ref.close()
            # Remove the zipfile
            os.remove(path)

    logger.info('Downloading session files')
    # Get project sessions
    project_sessions = fw.get_project_sessions(project_id)
    for proj_ses in project_sessions:
        # Get true session, in order to access file info
        session = fw.get_session(proj_ses['_id'])
        # Check if session contains files
        # Iterate over any session files
        for f in session.get('files', []):
            # Ensure that the folder exists...
            path = define_path(outdir, f, namespace)
            # Download the file
            fw.download_file_from_session(session['_id'], f['name'], path)

        logger.info('Downloading acquisition files')
        # Get acquisitions
        session_acqs = fw.get_session_acquisitions(proj_ses['_id'])
        for ses_acq in session_acqs:
            # Get true session, in order to access file info
            acq = fw.get_acquisition(ses_acq['_id'])
            # Iterate over acquistion files
            for f in acq.get('files', []):
                # Ensure that the folder exists...
                path = define_path(outdir, f, namespace)
                # Download the file
                fw.download_file_from_acquisition(acq['_id'], f['name'], path)

if __name__ == '__main__':
    ### Read in arguments
    parser = argparse.ArgumentParser(description='BIDS Directory Upload')
    parser.add_argument('--bids-dir', dest='bids_dir', action='store',
            required=True, help='Name of directory in which to download BIDS hierarchy. \
                    NOTE: Directory must be empty.')
    parser.add_argument('--api-key', dest='api_key', action='store',
            required=True, help='API key')
    parser.add_argument('-p', dest='project_label', action='store',
            required=False, default=None, help='Project Label on Flywheel instance')
    args = parser.parse_args()

    ### Prep
    # Check directory name - ensure it exists
    validate_dirname(args.bids_dir)
    # Check API key - raises Error if key is invalid
    fw = flywheel.Flywheel(args.api_key)

    # Get project Id from label
    project_id = validate_project_label(fw, args.project_label)

    ### Download BIDS project
    download_bids_dir(fw, project_id, args.bids_dir)

    # Validate the downloaded directory
    #   Go one more step into the hierarchy to pass to the validator...
    dirs = os.listdir(args.bids_dir)
    rootdir = os.path.join(args.bids_dir, dirs[0])
    utils.validate_bids(rootdir)
