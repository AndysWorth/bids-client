import argparse
import logging
import json
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
    logger.info('Verify download directory exists')

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

def parse_bool(v):
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v != 0

    return str(v).lower() == 'true'

def get_metadata(ctx, namespace):
    # Check if 'info' in f object
    if 'info' not in ctx:
        return None
    # Check if namespace ('BIDS') in f object
    if namespace not in ctx['info']:
        return None
    # Check if 'info.BIDS' == 'NA'
    if ctx['info'][namespace] == 'NA':
        return None

    return ctx['info'][namespace]

def is_file_excluded(f, namespace, src_data):
    metadata = get_metadata(f, namespace)
    if not metadata:
        return True

    if parse_bool(metadata.get('exclude', False)):
        return True

    if not src_data:
        path = metadata.get('Path')
        if path and path.startswith('sourcedata'):
            return True

    return False

def is_container_excluded(container, namespace):
    return isinstance(container.get('info', {}).get(namespace, {}), dict) and container.get('info', {}).get(namespace, {}).get('Ignore')

def warn_if_bids_invalid(f, namespace):
    """
    Logs a warning iff info.BIDS.valid = false
    """
    metadata = get_metadata(f, namespace)
    if not metadata or metadata.get('valid') == None:
        return
    elif not parse_bool(metadata.get('valid')):
        logger.warn('File {} is not valid: {}'.format(metadata.get('Filename'), metadata.get('error_message')))

def define_path(outdir, f, namespace):
    """"""
    metadata = get_metadata(f, namespace)
    if not metadata:
        full_filename = ''
    elif metadata.get('Filename'):
        # Ensure that the folder exists...
        full_path = os.path.join(outdir,
                metadata['Path'])
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        # Define path to download file to...
        full_filename = os.path.join(full_path, metadata['Filename'])
    else:
        full_filename = ''

    return full_filename

def get_folder(f, namespace):
    metadata = get_metadata(f, namespace)
    if not metadata:
        return ''

    return metadata.get('Folder')

def create_json(meta_info, path, namespace):
    """
    Given a dictionary of the meta info
        and the path, creates a JSON file
        with the bids info

    namespace in the template namespace,
        in this case it is 'BIDS'

    """
    # Remove the 'BIDS' value from info
    try:
        ns_data = meta_info.pop(namespace)
    except:
        ns_data = {}

    # If meta info is empty, simply return
    if not meta_info:
        return

    # If the file is functional,
    #   move the 'TaskName' from 'BIDS'
    #   to the top level
    if '/func/' in path:
         meta_info['TaskName'] = ns_data['Task']

    # Remove extension of path and replace with .json
    ext = utils.get_extension(path)
    new_path = re.sub(ext, '.json', path)

    # Write out contents to JSON file
    with open(new_path, 'w') as outfile:
        json.dump(meta_info, outfile,
                sort_keys=True, indent=4)

def download_bids_files(fw, filepath_downloads, dry_run):
    # Download all project files
    logger.info('Downloading project files')
    for f in filepath_downloads['project']:
        args = filepath_downloads['project'][f]
        logger.info('Downloading project file: {0}'.format(args[1]))
        # For dry run, don't actually download
        if dry_run:
            logger.info('  to {0}'.format(args[2]))
            continue
        fw.download_file_from_project(*args)

        # If zipfile is attached to project, unzip...
        path = args[2]
        zip_pattern = re.compile('[a-zA-Z0-9]+(.zip)')
        zip_dirname = path[:-4]
        if zip_pattern.search(path):
            zip_ref = zipfile.ZipFile(path, 'r')
            zip_ref.extractall(zip_dirname)
            zip_ref.close()
            # Remove the zipfile
            os.remove(path)

    # Download all session files
    logger.info('Downloading session files')
    for f in filepath_downloads['session']:
        args = filepath_downloads['session'][f]
        logger.info('Downloading session file: {0}'.format(args[1]))
        # For dry run, don't actually download
        if dry_run:
            logger.info('  to {0}'.format(args[2]))
            continue
        fw.download_file_from_session(*args)

    # Download all acquisition files
    logger.info('Downloading acquisition files')
    for f in filepath_downloads['acquisition']:
        args = filepath_downloads['acquisition'][f]
        # Download the file
        logger.info('Downloading acquisition file: {0}'.format(args[1]))

        # For dry run, don't actually download
        if dry_run:
            logger.info('  to {0}'.format(args[2]))
            continue

        fw.download_file_from_acquisition(*args)

    # Creating all JSON sidecar files
    logger.info('Creating sidecar files')
    for f in filepath_downloads['sidecars']:
        args = filepath_downloads['sidecars'][f]
        # Download the file
        logger.info('Creating sidecar file: {0}'.format(args[1]))

        # For dry run, don't actually download
        if dry_run:
            logger.info('  to {0}'.format(args[1]))
            continue

        create_json(*args)

def download_bids_dir(fw, project_id, outdir, src_data=False,
        dry_run=False, subjects=[], sessions=[], folders=[]):
    """

    fw: Flywheel client
    project_id: Label of the project to download
    outdir: path to directory to download files to, string
    src_data: Option to include sourcedata when downloading

    """

    # Define namespace
    namespace = 'BIDS'

    # Files and the corresponding download arguments
    filepath_downloads = {
        'project':{},
        'session':{},
        'acquisition':{},
        'sidecars':{}
    }

    # Get project
    project = fw.get_project(project_id)

    logger.info('Processing project files')
    # Iterate over any project files
    valid = True
    for f in project.get('files', []):
        # Don't exclude any files that specify exclusion
        if is_file_excluded(f, namespace, src_data):
            continue

        warn_if_bids_invalid(f, namespace)

        # Define path - ensure that the folder exists...
        path = define_path(outdir, f, namespace)
        # If path is not defined (an empty string) move onto next file
        if not path:
            continue

        # For dry run, don't actually download
        if path in filepath_downloads['project']:
            logger.error('Multiple files with path {0}:\n\t{1} and\n\t{2}'.format(path, f['name'], filepath_downloads['project'][path][1]))
            valid = False

        filepath_downloads['project'][path] = (project['_id'], f['name'], path)

    ## Create dataset_description.json filepath_download
    path = os.path.join(outdir, 'dataset_description.json')
    filepath_downloads['sidecars'][path] = (project['info'][namespace], path, namespace)

    logger.info('Processing session files')
    # Get project sessions
    project_sessions = fw.get_project_sessions(project_id)
    for proj_ses in project_sessions:
        # Skip session if we're filtering to the list of sessions
        if sessions and proj_ses.get('label') not in sessions:
            continue

        # Skip session if BIDS.Ignore is True
        if is_container_excluded(proj_ses, namespace):
            continue

        # Skip subject if we're filtering subjects
        if subjects:
            subj_code = proj_ses.get('subject', {}).get('code')
            if subj_code not in subjects:
                continue

        # Get true session, in order to access file info
        session = fw.get_session(proj_ses['_id'])
        # Check if session contains files
        # Iterate over any session files
        for f in session.get('files', []):
            # Don't exclude any files that specify exclusion
            if is_file_excluded(f, namespace, src_data):
                continue

            warn_if_bids_invalid(f, namespace)

            # Define path - ensure that the folder exists...
            path = define_path(outdir, f, namespace)
            # If path is not defined (an empty string) move onto next file
            if not path:
                continue

            if path in filepath_downloads['session']:
                logger.error('Multiple files with path {0}:\n\t{1} and\n\t{2}'.format(path, f['name'], filepath_downloads['session'][path][1]))
                valid = False

            filepath_downloads['session'][path] = (session['_id'], f['name'], path)

        logger.info('Processing acquisition files')
        # Get acquisitions
        session_acqs = fw.get_session_acquisitions(proj_ses['_id'])
        for ses_acq in session_acqs:

            # Skip if BIDS.Ignore is True
            if is_container_excluded(ses_acq, namespace):
                continue
            # Get true acquisition, in order to access file info
            acq = fw.get_acquisition(ses_acq['_id'])
            # Iterate over acquistion files
            for f in acq.get('files', []):
                # Don't exclude any files that specify exclusion
                if is_file_excluded(f, namespace, src_data):
                    continue

                warn_if_bids_invalid(f, namespace)

                # Skip any folders not in the skip-list (if there is a skip list)
                if folders:
                    folder = get_folder(f, namespace)
                    if folder not in folders:
                        continue

                # Define path - ensure that the folder exists...
                path = define_path(outdir, f, namespace)
                # If path is not defined (an empty string) move onto next file
                if not path:
                    continue
                if path in filepath_downloads['acquisition']:
                    logger.error('Multiple files with path {0}:\n\t{1} and\n\t{2}'.format(path, f['name'], filepath_downloads['acquisition'][path][1]))
                    valid = False

                filepath_downloads['acquisition'][path] = (acq['_id'], f['name'], path)

                # Create the sidecar JSON filepath_download
                filepath_downloads['sidecars'][path] = (f['info'], path, namespace)

    if not valid:
        sys.exit(1)

    download_bids_files(fw, filepath_downloads, dry_run)

if __name__ == '__main__':
    ### Read in arguments
    parser = argparse.ArgumentParser(description='BIDS Directory Export')
    parser.add_argument('--bids-dir', dest='bids_dir', action='store',
            required=True, help='Name of directory in which to download BIDS hierarchy. \
                    NOTE: Directory must be empty.')
    parser.add_argument('--api-key', dest='api_key', action='store',
            required=True, help='API key')
    parser.add_argument('--source-data', dest='source_data', action='store_true',
            default=False, required=False, help='Include source data in BIDS export')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
            default=False, required=False, help='Don\'t actually export any data, just print what would be exported')
    parser.add_argument('--subject', dest='subjects', action='append', help='Limit export to the given subject')
    parser.add_argument('--session', dest='sessions', action='append', help='Limit export to the given session name')
    parser.add_argument('--folder', dest='folders', action='append', help='Limit export to the given folder. (e.g. func)')
    parser.add_argument('-p', dest='project_label', action='store',
            required=False, default=None, help='Project Label on Flywheel instance')
    args = parser.parse_args()

    ### Prep
    # Check directory name - ensure it exists
    validate_dirname(args.bids_dir)
    # Check API key - raises Error if key is invalid
    fw = flywheel.Flywheel(args.api_key)

    # Get project Id from label
    project_id = utils.validate_project_label(fw, args.project_label)

    ### Download BIDS project
    download_bids_dir(fw, project_id, args.bids_dir, src_data=args.source_data,
            dry_run=args.dry_run, subjects=args.subjects, sessions=args.sessions, folders=args.folders)

    # Validate the downloaded directory
    #   Go one more step into the hierarchy to pass to the validator...
    if not args.dry_run:
        utils.validate_bids(args.bids_dir)
