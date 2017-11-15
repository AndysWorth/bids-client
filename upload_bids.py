import argparse
import logging
import os
import sys
import shutil
import re


import flywheel

from supporting_files import bidsify_flywheel, templates, classifications


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bids-uploader')

def validate_dirname(dirname):
    """
    Check the following criteria to ensure 'dirname' is valid
        - dirname exists
        - dirname is a directory
    If criteria not met, raise an error
    """
    logger.info('Validating BIDS directory')

    # Check dirname exists
    if not os.path.exists(dirname):
        logger.error('Path (%s) does not exist' % dirname)
        sys.exit(1)

    # Check dirname is a directory
    if not os.path.isdir(dirname):
        logger.error('Path (%s) is not a directory' % dirname)
        sys.exit(1)

def parse_bids_dir(bids_dir):
    """
    Creates a nested dictionary that represents the folder structure of bids_dir

    if '/tmp/ds001' is bids dir passed, 'ds001' is first key and is the project name...
    """
    ## Read in BIDS hierarchy
    bids_hierarchy = {}
    bids_dir = bids_dir.rstrip(os.sep)
    start = bids_dir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(bids_dir):
        folders = path[start:].split(os.sep)
        subdir = {'files': files}
        parent = reduce(dict.get, folders[:-1], bids_hierarchy)
        parent[folders[-1]] = subdir

    return bids_hierarchy


def handle_project(fw, group_id, project_label):
    """ Returns a Flywheel project based on group_id and project_label

    If project exists, project will be retrieved,
     else project will be created 
    """
    # Get all projects
    existing_projs = fw.get_all_projects()
    # Determine if project_label with group_id already exists
    found = False
    for ep in existing_projs:
        if (ep['label'] == project_label) and (ep['group'] == group_id):
            logger.info('Project (%s) was found. Adding data to existing project.' % project_label)
            # project exists
            project = ep
            found = True
            break
    # If project does not exist, create project
    if not found:
        logger.info('Project (%s) not found. Creating new project for group %s.' % (project_label, group_id))
        project_id = fw.add_project({'label': project_label, 'group': group_id})
        project = fw.get_project(project_id)

    return project

def handle_session(fw, project_id, session_label, subject_code):
    """ Returns a Flywheel session based on project_id and session_label

    If session exists, session will be retrieved,
     else session will be created 
    """
    # Get all sessions
    existing_sessions = fw.get_project_sessions(project_id)
    # Determine if session_label within project project_id already exists, with same subject_code...
    found = False
    for es in existing_sessions:
        if (es['label'] == session_label) and (es['subject']['code'] == subject_code):
            logger.info('Session (%s) for subject (%s) was found. Adding data to existing session.' % (session_label, subject_code))
            # Session exists
            session = es
            found = True
            break
    # If session does not exist, create new session
    if not found:
        logger.info('Session (%s) not found. Creating new session for project %s.' % (session_label, project_id))
        session_id = fw.add_session({'label': session_label, 'project': project_id,
                                    'subject': {'code': subject_code}})
        session = fw.get_session(session_id)

    return session

def handle_acquisition(fw, session_id, acquisition_label):
    """ Returns a Flywheel acquisition based on session_id and acquisition_label

    If acquisition exists, acquisition will be retrieved,
     else acquisition will be created 
    """
    # Get all sessions
    existing_acquisitions = fw.get_session_acquisitions(session_id)
    # Determine if acquisition_label within project project_id already exists
    found = False
    for ea in existing_acquisitions:
        if ea['label'] == acquisition_label:
            logger.info('Acquisition (%s) was found. Adding data to existing acquisition.' % acquisition_label)
            # Acquisition exists
            acquisition = ea
            found = True
            break
    # If session does not exist, create new session
    if not found:
        logger.info('Acquisition (%s) not found. Creating new acquisition for session %s.' % (acquisition_label, session_id))
        acquisition_id = fw.add_acquisition({'label': acquisition_label, 'session': session_id})
        acquisition = fw.get_acquisition(acquisition_id)

    return acquisition

def upload_project_file(fw, context, full_fname):
    """"""
    # Upload file
    fw.upload_file_to_project(context['project']['_id'], full_fname)
    # Get project
    proj = fw.get_project(context['project']['_id'])
    # Return project file object
    return proj['files'][-1]

def upload_session_file(fw, context, full_fname):
    """"""
    # Upload file
    fw.upload_file_to_session(context['session']['_id'], full_fname)
    # Get session
    ses = fw.get_session(context['session']['_id'])
    # Return session file object
    return ses['files'][-1]

def upload_acquisition_file(fw, context, full_fname):
    """"""
    # Upload file
    fw.upload_file_to_acquisition(context['acquisition']['_id'], full_fname)

    ### Classify acquisition
    # Get classification based on filename
    classification = classify_acquisition(full_fname)
    # Assign classification
    if classification:
        fw.modify_acquisition_file(context['acquisition']['_id'],
              context['file']['name'],
           {'measurements': [classification]})

    # Get acquisition
    acq = fw.get_acquisition(context['acquisition']['_id'])
    # Return acquisition file object
    return acq['files'][-1]

def classify_acquisition(full_fname):
    """ Return classification of file based on filename"""

    # Get the folder and filename from the full filename
    parts = full_fname.split('/')
    folder = parts[-2]
    filename = parts[-1]
    # Get the modality label
    modality_ext = filename.split('_')[-1]
    # remove extension
    modality = modality_ext.split('.')[0]

    return classifications.classifications.get(folder).get(modality)

def get_extension(fname):
    """ Get extension

    If search returns a result, get value
    else, ext is None

    """
    ext = re.search('\.[A-Za-z0-9\._-]+',fname)
    if ext: ext = ext.group()
    return ext

def fill_in_properties(context, folder_name):
    """ """
    # Define the regex to use to find the property value from filename
    properties_regex = {
        'Ce': '_ce-[0-9a-zA-Z]+',
        'Rec': '_rec-[0-9a-zA-Z]+',
        'Run': '_run-[0-9]+',
        'Mod': '_mod-[0-9a-zA-Z]+',
        'Task': '_task-[0-9a-zA-Z]+',
        'Echo': '_echo-[0-9]+',
        'Dir': '_dir-[0-9a-zA-Z]+',
        'Modality': '_[0-9a-zA-Z]+%s' % context['ext']
    }

    # Get meta info
    meta_info = context['file']['info']
    # Get namespace
    namespace = 'BIDS'
    # Iterate over all of the keys within the info namespace ('BIDS')
    for mi in meta_info[namespace]:
        if mi == 'Folder':
            meta_info[namespace][mi] = folder_name
        elif mi == 'Filename':
            meta_info[namespace][mi] = context['file']['name']
        # Search for regex string within BIDS filename and populate meta_info
        else:
            tokens = re.compile(properties_regex[mi])
            token = tokens.search(context['file']['name'])
            if token:
                # Get the matched string
                result = token.group()
                # If meta_info is Modality 
                if mi == 'Modality':
                    value = result[1:-len(context['ext'])]
                # Get the value after the '-'
                else:
                    value = result.split('-')[-1]
                # If value as an 'index' instead of a 'label', make it an integer (for search)
                if mi in ['Run', 'Echo']:
                    value = int(value)
                # Assign value to meta_info
                meta_info[namespace][mi] = value

    return meta_info

def upload_bids_dir(fw, bids_hierarchy, group_id, rootdir):
    """

    """

    # Iterate
    # Initialize context object
    context = {
        'container_type': None,
        'parent_container_type': None,
        'project': None,
        'subject': None,
        'session': None,
        'acquisition': None,
        'file': None,
        'ext': None
    }

    # Iterate over BIDS hierarchy (first key will be top level dirname which we will use as the project label)
    for proj_label in bids_hierarchy:
        ## Validate the project (there is a function within upload_bids)
        #   (1) create a project OR (2) find an existing project by the project_label -- return project object
        context['container_type'] = 'project'
        context['project'] = handle_project(fw, group_id, proj_label)
        bidsify_flywheel.process_matching_templates(context)

        ### Iterate over project files - upload file and add meta data
        for fname in bids_hierarchy[proj_label].get('files'):
            ### Upload file
            # define full filename
            full_fname = os.path.join(rootdir, proj_label, fname)
            # Upload project file
            context['file'] = upload_project_file(fw, context, full_fname)
            # Update the context for this file
            context['container_type'] = 'file'
            context['parent_container_type'] = 'project'
            context['ext'] = get_extension(fname)
            # Identify the templates for the file and return file object
            context['file'] = bidsify_flywheel.process_matching_templates(context)
            # Update the meta info files w/ BIDS info from the filename...
            meta_info = fill_in_properties(context, proj_label)
            # Upload the meta info onto the project file
            fw.set_project_file_info(context['project']['_id'], fname, meta_info)

        ### Figure out which directories are subjects, and which are directories
        #       that should be zipped up and add to project
        # Get subjects
        subjects = [key for key in bids_hierarchy[proj_label] if 'sub' in key]
        # Get non-subject directories remaining
        dirs = [item for item in bids_hierarchy[proj_label] if item not in subjects and item != 'files']

        ### Iterate over project directories (that aren't 'sub' dirs) - zip up directory contents and add meta data
        for dirr in dirs:
            ### Zip and Upload file
            # define full dirname and zipname
            full_dname = os.path.join(rootdir, proj_label, dirr)
            full_zname = os.path.join(rootdir, proj_label, dirr + '.zip')
            shutil.make_archive(full_dname, 'zip', full_dname)
            # Upload project file
            context['file'] = upload_project_file(fw, context, full_zname)
            # remove the generated zipfile
            os.remove(full_zname)
            # Update the context for this file
            context['container_type'] = 'file'
            context['parent_container_type'] = 'project'
            context['ext'] = get_extension(full_zname)
            # Identify the templates for the file and return file object
            context['file'] = bidsify_flywheel.process_matching_templates(context)
            # Update the meta info files w/ BIDS info from the filename...
            meta_info = fill_in_properties(context, proj_label)
            # Upload the meta info onto the project file
            fw.set_project_file_info(context['project']['_id'], dirr+'.zip', meta_info)

        ### Iterate over subjects
        for subject_code in subjects:
            #   In BIDS, the session is optional, if not present - use subject_code as session_label
            # Get all keys that are session - 'ses-<session.label>'
            sessions = [key for key in bids_hierarchy[proj_label][subject_code] if 'ses' in key]
            # If no sessions, add session layer, just subject_label will be the subject_code
            if not sessions:
                sessions = [subject_code]
                bids_hierarchy[proj_label][subject_code] = {subject_code: bids_hierarchy[proj_label][subject_code]}

            ## Iterate over subject files
            # TODO/NOTE: How do we handle if there are files specific to the subject?
            #    since it's not a container currently??

            ### Iterate over sessions 
            for session_label in sessions:
                # Create Session
                context['session'] = handle_session(fw, context['project']['_id'], session_label, subject_code)
                # Hand off subject code
                context['subject'] = context['session']['subject']

                ## Iterate over session files - upload file and add meta data
                for fname in bids_hierarchy[proj_label][subject_code][session_label].get('files'):
                    ### Upload file
                    # define full filename
                    #   NOTE: If session_label and subject_code are the same, session label
                    #       is not actually present within the original directory structure
                    if session_label == subject_code:
                        full_fname = os.path.join(rootdir, proj_label, subject_code, fname)
                    else:
                        full_fname = os.path.join(rootdir, proj_label, subject_code, session_label, fname)
                    # Upload session file
                    context['file'] = upload_session_file(fw, context, full_fname)
                    # Update the context for this file
                    context['container_type'] = 'file'
                    context['parent_container_type'] = 'session'
                    context['ext'] = get_extension(fname)
                    # Identify the templates for the file and return file object
                    context['file'] = bidsify_flywheel.process_matching_templates(context)
                    # Update the meta info files w/ BIDS info from the filename...
                    meta_info = fill_in_properties(context, session_label)
                    # Upload the meta info onto the project file
                    fw.set_session_file_info(context['session']['_id'], fname, meta_info)

                ## Iterate over 'acquisitions' which are ['anat', 'func', 'fmap', 'dwi'...]
                #          NOTE: could there be any other dirs that would be handled differently?
                # get acquisitions
                acquisitions = [item for item in bids_hierarchy[proj_label][subject_code][session_label] if item != 'files']
                for acq_label in acquisitions:
                    # Create acquisition
                    context['acquisition'] = handle_acquisition(fw, context['session']['_id'], acq_label)

                    # Iterate over acquisition files -- upload file and add meta data
                    for fname in bids_hierarchy[proj_label][subject_code][session_label][acq_label].get('files'):
                        ### Upload file
                        # define full filename
                        #   NOTE: If session_label and subject_code are the same, session label
                        #       is not actually present within the original directory structure
                        if session_label == subject_code:
                            full_fname = os.path.join(rootdir, proj_label, subject_code, acq_label, fname)
                        else:
                            full_fname = os.path.join(rootdir, proj_label, subject_code, session_label, acq_label, fname)
                        # Place filename in context
                        context['file'] = {u'name': fname}
                        # Upload acquisition file
                        context['file'] = upload_acquisition_file(fw, context, full_fname)
                        # Update the context for this file
                        context['container_type'] = 'file'
                        context['parent_container_type'] = 'acquisition'
                        context['ext'] = get_extension(fname)
                        # Identify the templates for the file and return file object
                        context['file'] = bidsify_flywheel.process_matching_templates(context)
                        # Update the meta info files w/ BIDS info from the filename...
                        meta_info = fill_in_properties(context, acq_label)
                        # Upload the meta info onto the project file
                        fw.set_acquisition_file_info(context['acquisition']['_id'], fname, meta_info)

# Scope of project
#   Take a BIDS dataset, import into flywheel, be able to preserve

if __name__ == '__main__':
    ### Read in arguments
    parser = argparse.ArgumentParser(description='BIDS Directory Upload')
    parser.add_argument('--bids-dir', dest='bids_dir', action='store',
            required=True, help='BIDS directory')
    parser.add_argument('--api-key', dest='api_key', action='store',
            required=True, help='API key')
    parser.add_argument('-g', dest='group_id', action='store',
            required=False, default=None, help='Group ID on Flywheel instance')
    parser.add_argument('-p', dest='project_label', action='store',
            required=False, default=None, help='Project Label on Flywheel instance')
    args = parser.parse_args()

    ### Prep
    # Check directory name - ensure it exists
    validate_dirname(args.bids_dir)
    # Check API key - raises Error if key is invalid
    fw = flywheel.Flywheel(args.api_key)

    ### Read in hierarchy & Validate as BIDS
    # parse BIDS dir
    bids_hierarchy = parse_bids_dir(args.bids_dir)
    # TODO: Determine if group id and project label are present
    # group_id, project_label =  (bids_hierarchy, args.group_id, args.project_label)
    # TODO: determine if hierarchy is valid BIDS
    #(bids_hierarchy)

    # TODO: Define group_id
    group_id = 'jr'


    ### Upload BIDS directory
    # define rootdir
    rootdir = os.path.dirname(args.bids_dir)
    # upload bids dir
    upload_bids_dir(fw, bids_hierarchy, group_id, rootdir)
