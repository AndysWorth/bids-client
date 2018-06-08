import argparse
import csv
import json
import logging
import os
import re
import shutil
import sys

import flywheel

from six.moves import reduce

from .supporting_files import bidsify_flywheel, classifications, utils
from .supporting_files.templates import BIDS_TEMPLATE as template


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bids-uploader')

def validate_dirname(dirname):
    """
    Check the following criteria to ensure 'dirname' is valid
        - dirname exists
        - dirname is a directory
    If criteria not met, raise an error
    """
    logger.info('Verifying directory exists')

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

def handle_project_label(bids_hierarchy, project_label_cli, rootdir):
    """ Determines the values for the group_id and project_label information

    Below is the expected hierarchy for the 'bids_hiearchy':

            project_label: {
                    sub-AAA: {},
                    sub-BBB: {},
                    ...
                }

    project_label_cli is a value optionally defined by user from command line

    returns bids_hierarchy as expected structure with the project label within the hierarchy

    raises error if project_label is not defined within bids_hierarchy
         structure AND not passed through the command line

    """
    # Initialize sub
    top_level = False
    second_level = False
    # Define sub directory pattern
    subdir_pattern = re.compile('sub-[a-zA-Z0-9]+')

    # Iterate over top level keys in bids hierarchy
    for k in bids_hierarchy:
        # If sub-YY pattern found at topmost level, project label is not defined
        if subdir_pattern.search(k):
            # subdirs found
            top_level = True
            break
        # Iterate over second level keys in bids hierarchy
        for kk in bids_hierarchy[k]:
            # If sub-YY pattern found, then project_label is defined
            if subdir_pattern.search(kk):
                # subdirs found
                second_level = True

    # If sub-YY directories found at top level,
    #   project_label_cli must be defined
    if top_level:
        if project_label_cli:
            bids_hierarchy = {project_label_cli: bids_hierarchy}
            bids_hierarchy[project_label_cli]['files'] = []
            rootdir = os.path.dirname(rootdir)
        # If not defined, raise an error! project label is not defined
        else:
            logger.error('Project label cannot be determined')
            sys.exit(1)

    # If sub-YY directories found at second level
    #   project_label_cli does not NEED to be defined (no error raised)
    if second_level and project_label_cli:
        bids_hierarchy[project_label_cli] = bids_hierarchy.pop(k)

    # If sub-YY directories are not found
    if not (top_level or second_level):
        logger.error('Did not find subject directories within hierarchy')
        sys.exit(1)

    return bids_hierarchy, rootdir


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

def handle_session(fw, project_id, session_name, subject_name):
    """ Returns a Flywheel session based on project_id and session_label

    If session exists, session will be retrieved,
     else session will be created

    """
    # Get all sessions
    existing_sessions = fw.get_project_sessions(project_id)
    # Determine if session_name within project project_id already exists, with same subject_name...
    found = False
    for es in existing_sessions:
        if (es['label'] == session_name) and (es['subject']['code'] == subject_name):
            logger.info('Session (%s) for subject (%s) was found. Adding data to existing session.' % (session_name, subject_name))
            # Session exists
            session = es
            found = True
            break
    # If session does not exist, create new session
    if not found:
        logger.info('Session (%s) not found. Creating new session for project %s.' % (session_name, project_id))

        session_id = fw.add_session({
            'label': session_name,
            'project': project_id,
            'subject': {'code': subject_name},
            'info': { template.namespace: {} }
        })
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
    # If acquisition does not exist, create new session
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
        update = {
            'modality': 'MR',
            'replace': classification
        }
        fw.modify_acquisition_file_classification(context['acquisition']['_id'],
              context['file']['name'], update)

    # Get acquisition
    acq = fw.get_acquisition(context['acquisition']['_id'])
    # Return acquisition file object
    return acq['files'][-1]

def determine_acquisition_label(foldername, fname, hierarchy_type):
    """ """
    # If bids hierarchy, the acquisition label is
    if hierarchy_type == 'BIDS':
        acq_label = foldername
    else:
        # Get acq_label from file basename
        #  remove extension from the filename
        fname = fname.split('.')[0]
        #  split up filename into parts, removing the final part, the Modality
        parts = fname.split('_')
        # If the last section of the filename matches 'bold', 'events', 'physio' or 'stim', remove!
        if parts[-1] in ['bold', 'events', 'physio', 'stim']:
            parts = parts[:-1]
        # Rejoin filename parts to form acquisition label
        acq_label = '_'.join(parts)
        # Remove any of the following values
        for pattern in ['sub-[0-9a-zA-Z]+_', 'ses-[0-9a-zA-Z]+_', '_recording-[0-9a-zA-Z]+']:
            acq_label = re.sub(pattern, '', acq_label)

    return acq_label

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

    result = classifications.classifications.get(folder).get(modality)

    if result:
        for k in result.keys():
            v = result[k]
            if not isinstance(v, list):
                result[k] = [v]

    return result



def fill_in_properties(context, path):
    """ """
    # Define the regex to use to find the property value from filename
    properties_regex = {
        'Acq': '_acq-[a-zA-Z0-9]+',
        'Ce': '_ce-[a-zA-Z0-9]+',
        'Rec': '_rec-[a-zA-Z0-9]+',
        'Run': '_run-[0-9]+',
        'Mod': '_mod-[a-zA-Z0-9]+',
        'Task': '_task-[a-zA-Z0-9]+',
        'Echo': '_echo-[0-9]+',
        'Dir': '_dir-[a-zA-Z0-9]+',
        'Recording': '_recording-[a-zA-Z0-9]+',
        'Modality': '_[a-zA-Z0-9]+%s' % context['ext']
    }

    # Get meta info
    meta_info = context['file']['info']
    # Get namespace
    namespace = template.namespace
    # Iterate over all of the keys within the info namespace ('BIDS')
    for mi in meta_info[namespace]:
        if mi == 'Filename':
            meta_info[namespace][mi] = context['file']['name']
        elif mi == 'Folder':
            meta_info[namespace][mi] = path.split('/')[-1]
        elif mi == 'Path':
            meta_info[namespace][mi] = path
            # Search for regex string within BIDS filename and populate meta_info
        elif mi in properties_regex:
            tokens = re.compile(properties_regex[mi])
            token = tokens.search(context['file']['name'])
            if token:
                # Get the matched string
                result = token.group()
                # If meta_info is Modality, get the value before the extension...
                if mi == 'Modality':
                    value = result[1:-len(context['ext'])]
                # Get the value after the '-'
                else:
                    value = result.split('-')[-1]
                # If value as an 'index' instead of a 'label', make it an integer (for search)
                if mi in ['Run', 'Echo']:
                    value = str(value)
                # Assign value to meta_info
                meta_info[namespace][mi] = value

    return meta_info

def upload_bids_dir(fw, bids_hierarchy, group_id, rootdir, hierarchy_type):
    """

    fw: Flywheel client
    bids_hierarchy: BIDS hierarchy, dict
    rootdir: path to files, string
    hierarchy_type: either 'Flywheel' or 'BIDS'
            if 'Flywheel', the base filename is used as the acquisition label
            if 'BIDS', the BIDS foldername (anat,func,dwi etc...) is used as the acquisition label

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

    # Collect files to be parsed at the end
    files_of_interest = {
            }

    # Iterate over BIDS hierarchy (first key will be top level dirname which we will use as the project label)
    for proj_label in bids_hierarchy:
        ## Validate the project
        #   (1) create a project OR (2) find an existing project by the project_label -- return project object
        context['container_type'] = 'project'
        context['project'] = handle_project(fw, group_id, proj_label)
        context['project'] = bidsify_flywheel.process_matching_templates(context, template, upload=True)
        fw.modify_project(context['project']['_id'], {'info': {template.namespace: context['project']['info'][template.namespace]}})

        ### Iterate over project files - upload file and add meta data
        for fname in bids_hierarchy[proj_label].get('files'):
            # Exclude filenames that begin with .
            if fname.startswith('.'):
                continue
            ### Upload file
            # define full filename
            full_fname = os.path.join(rootdir, fname)
            # Don't upload json sidecars
            if '.json' in fname:
                files_of_interest[fname] = {
                        '_id': context['project']['_id'],
                        'id_type': 'project',
                        'full_filename': full_fname
                        }
                continue
            # Upload project file
            context['file'] = upload_project_file(fw, context, full_fname)
            # Update the context for this file
            context['container_type'] = 'file'
            context['parent_container_type'] = 'project'
            context['ext'] = utils.get_extension(fname)
            # Identify the templates for the file and return file object
            context['file'] = bidsify_flywheel.process_matching_templates(context, template, upload=True)
            # Update the meta info files w/ BIDS info from the filename...
            full_path = ''
            meta_info = fill_in_properties(context, full_path)
            # Upload the meta info onto the project file
            fw.set_project_file_info(context['project']['_id'], fname, meta_info)

            # Check if project files are of interest (to be parsed later)
            #    Interested in participants.tsv or any JSON file
            if (fname == 'participants.tsv'):
                files_of_interest[fname] = {
                        '_id': context['project']['_id'],
                        'id_type': 'project',
                        'full_filename': full_fname
                        }

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
            full_dname = os.path.join(rootdir, dirr)
            full_zname = os.path.join(rootdir, dirr + '.zip')
            shutil.make_archive(full_dname, 'zip', full_dname)
            # Upload project file
            context['file'] = upload_project_file(fw, context, full_zname)
            # remove the generated zipfile
            os.remove(full_zname)
            # Update the context for this file
            context['container_type'] = 'file'
            context['parent_container_type'] = 'project'
            context['ext'] = utils.get_extension(full_zname)
            # Identify the templates for the file and return file object
            context['file'] = bidsify_flywheel.process_matching_templates(context, template, upload=True)
            # Update the meta info files w/ BIDS info from the filename...
            full_path = ''
            meta_info = fill_in_properties(context, full_path)
            # Upload the meta info onto the project file
            fw.set_project_file_info(context['project']['_id'], dirr+'.zip', meta_info)

        ### Iterate over subjects
        for subject_code in subjects:
            #   In BIDS, the session is optional, if not present - use subject_code as session_label
            # Get all keys that are session - 'ses-<session.label>'
            sessions = [key for key in bids_hierarchy[proj_label][subject_code] if 'ses' in key]
            # If no sessions, add session layer, just subject_label will be the subject_code
            if not sessions:
                sessions = ['ses-']
                bids_hierarchy[proj_label][subject_code] = {'ses-': bids_hierarchy[proj_label][subject_code]}

            ## Iterate over subject files
            # NOTE: Attaching files to project instead of subject....
            subject_files = bids_hierarchy[proj_label][subject_code].get('files')
            if subject_files:
                for fname in bids_hierarchy[proj_label][subject_code].get('files'):
                    # Exclude filenames that begin with .
                    if fname.startswith('.'):
                        continue
                    ### Upload file
                    # define full filename
                    full_fname = os.path.join(rootdir, subject_code, fname)
                    # Don't upload sidecars
                    if ('.json' in fname):
                        files_of_interest[fname] = {
                                '_id': context['project']['_id'],
                                'id_type': 'project',
                                'full_filename': full_fname
                                }
                        continue
                    # Upload project file ## TODO: once subjects are containers, add new method to upload to subject
                    context['file'] = upload_project_file(fw, context, full_fname)
                    # Update the context for this file
                    context['container_type'] = 'file'
                    context['parent_container_type'] = 'project' # TODO: once subjects are containers, change this to 'subject'
                    context['ext'] = utils.get_extension(fname)
                    # Identify the templates for the file and return file object
                    context['file'] = bidsify_flywheel.process_matching_templates(context, template, upload=True)
                    # Update the meta info files w/ BIDS info from the filename...
                    full_path = subject_code
                    meta_info = fill_in_properties(context, full_path)
                    # Upload the meta info onto the project file
                    fw.set_project_file_info(context['project']['_id'], fname, meta_info)

                    # Check if any subject files are of interest (to be parsed later)
                    #   interested in _sessions files and JSON files
                    val = '%s_sessions.tsv' % subject_code
                    if (fname == val) or ('.json' in fname):
                        files_of_interest[fname] = {
                                '_id': context['project']['_id'],
                                'id_type': 'project',
                                'full_filename': full_fname
                                }

            ### Iterate over sessions
            for session_label in sessions:
                # Create Session
                context['session'] = handle_session(fw, context['project']['_id'], session_label, subject_code)
                # Hand off subject info to context
                context['subject'] = context['session']['subject']

                ## Iterate over session files - upload file and add meta data
                for fname in bids_hierarchy[proj_label][subject_code][session_label].get('files'):
                    # Exclude filenames that begin with .
                    if fname.startswith('.'):
                        continue
                    ### Upload file
                    # define full filename
                    #   NOTE: If session_label equals 'ses-', session label is not
                    #       actually present within the original directory structure
                    if session_label == 'ses-':
                        full_fname = os.path.join(rootdir, subject_code, fname)
                        full_path = subject_code
                    else:
                        full_fname = os.path.join(rootdir, subject_code, session_label, fname)
                        full_path = os.path.join(subject_code, session_label)

                    # Don't upload sidecars
                    if ('.json' in fname):
                        files_of_interest[fname] = {
                                '_id': context['session']['_id'],
                                'id_type': 'session',
                                'full_filename': full_fname
                                }
                        continue
                    # Upload session file
                    context['file'] = upload_session_file(fw, context, full_fname)
                    # Update the context for this file
                    context['container_type'] = 'file'
                    context['parent_container_type'] = 'session'
                    context['ext'] = utils.get_extension(fname)
                    # Identify the templates for the file and return file object
                    context['file'] = bidsify_flywheel.process_matching_templates(context, template, upload=True)
                    # Update the meta info files w/ BIDS info from the filename...
                    meta_info = fill_in_properties(context, full_path)
                    # Upload the meta info onto the project file
                    fw.set_session_file_info(context['session']['_id'], fname, meta_info)

                    # Check if any session files are of interest (to be parsed later)
                    #   interested in _scans.tsv and JSON files
                    val = '%s_%s_scans.tsv' % (subject_code, session_label)
                    if (fname == val):
                        files_of_interest[fname] = {
                                    '_id': context['session']['_id'],
                                    'id_type': 'session',
                                    'full_filename': full_fname
                                    }

                ## Iterate over 'folders' which are ['anat', 'func', 'fmap', 'dwi'...]
                #          NOTE: could there be any other dirs that would be handled differently?
                # get folders
                folders = [item for item in bids_hierarchy[proj_label][subject_code][session_label] if item != 'files']
                for foldername in folders:

                    # Iterate over acquisition files -- upload file and add meta data
                    for fname in bids_hierarchy[proj_label][subject_code][session_label][foldername].get('files'):
                        # Exclude filenames that begin with .
                        if fname.startswith('.'):
                            continue
                        # Determine acquisition label -- it can either be the folder name OR the basename of the file...
                        acq_label = determine_acquisition_label(foldername, fname, hierarchy_type)
                        # Create acquisition
                        context['acquisition'] = handle_acquisition(fw, context['session']['_id'], acq_label)
                        ### Upload file
                        # define full filename
                        #   NOTE: If session_label equals 'ses-', session label is not
                        #       actually present within the original directory structure
                        if session_label == 'ses-':
                            full_fname = os.path.join(rootdir, subject_code, foldername, fname)
                            full_path = os.path.join(subject_code, foldername)
                        else:
                            full_fname = os.path.join(rootdir, subject_code, session_label, foldername, fname)
                            full_path = os.path.join(subject_code, session_label, foldername)

                        # Check if any acquisition files are of interest (to be parsed later)
                        #   interested in JSON files
                        if '.json' in fname:
                            files_of_interest[fname] = {
                                    '_id': context['acquisition']['_id'],
                                    'id_type': 'acquisition',
                                    'full_filename': full_fname
                                    }
                            continue

                        # Place filename in context
                        context['file'] = {u'name': fname}
                        # Upload acquisition file
                        context['file'] = upload_acquisition_file(fw, context, full_fname)
                        # Update the context for this file
                        context['container_type'] = 'file'
                        context['parent_container_type'] = 'acquisition'
                        context['ext'] = utils.get_extension(fname)
                        # Identify the templates for the file and return file object
                        context['file'] = bidsify_flywheel.process_matching_templates(context, template, upload=True)
                        # Check that the file matched a template
                        if context['file'].get('info'):
                            # Update the meta info files w/ BIDS info from the filename and foldername...
                            meta_info = fill_in_properties(context, full_path)
                            # Upload the meta info onto the project file
                            fw.set_acquisition_file_info(context['acquisition']['_id'], fname, meta_info)

    return files_of_interest

def parse_json(filename):
    """ """
    with open(filename) as json_data:
        contents = json.load(json_data)
    return contents


def compare_json_to_file(json_filename, filename):
    """

    Determine if a JSON file's contents apply to a filename

    json_filename: Name of the json filename
    filename: Name of the file in question, does
        the json file contents apply to this file?

    i.e.
        The following json_filename...

            'task-rest_acq-fullbrain_bold.json'

        ...applies to the following filenames:

        'sub-01_ses-1_task-rest_acq-fullbrain_run-1_bold.nii.gz'
        'sub-01_ses-1_task-rest_acq-fullbrain_run-2_bold.nii.gz'
        'sub-01_ses-2_task-rest_acq-fullbrain_run-1_bold.nii.gz'
        'sub-01_ses-2_task-rest_acq-fullbrain_run-2_bold.nii.gz'

    NOTE: files must be a nifti or tsv.gz file...

    """
    # First check if file is a nifti file...
    if ('.nii' not in filename) and ('.tsv.gz' not in filename):
        match = False
    else:
        # Remove .json extension from filename
        json_filename = re.sub('.json', '', json_filename)
        # Split json filename up into components
        components = json_filename.split('_')
        # Iterate over all components within JSON file,
        #   if any of them are missing, match is False
        match = True
        for c in components:
            if c not in filename:
                match = False
                break

    return match

def attach_json(fw, file_info):
    # Parse JSON file
    contents = parse_json(file_info['full_filename'])
    # Attach parsed JSON to project
    if 'dataset_description.json' in file_info['full_filename']:
        proj = fw.get_project(file_info['_id'])
        proj.get('info').get(template.namespace).update(contents)
        fw.modify_project(file_info['_id'], {'info': {template.namespace: proj.get('info').get(template.namespace)}})
    # Otherwise... it's a JSON file that should be assigned to acquisition file(s)
    else:
        # Figure out which acquisition files within PROJECT should have JSON info attached...
        if (file_info['id_type'] == 'project'):
            # Get sessions within project
            proj_sess = fw.get_project_sessions(file_info['_id'])
            for proj_ses in proj_sess:
                # Get acquisitions within session
                ses_acqs = fw.get_session_acquisitions(proj_ses['_id'])
                for ses_acq in ses_acqs:
                    # Iterate over every acquisition file
                    for f in ses_acq['files']:
                        # Determine if json file components are all within the acq filename
                        if compare_json_to_file(os.path.basename(file_info['full_filename']), f['name']):
                            # JSON matches to file - assign json contents as file meta info
                            f["info"].update(contents)
                            fw.set_acquisition_file_info(
                                    ses_acq['_id'],
                                    f['name'],
                                    f['info'])

        # Figure out which acquisition files within SESSION should have JSON info attached...
        elif (file_info['id_type'] == 'session'):
            # Get session and iterate over every acquisition file
            ses_acqs = fw.get_session_acquisitions(file_info['_id'])
            for ses_acq in ses_acqs:
                for f in ses_acq['files']:
                    # Determine if json file components are all within the acq filename
                    if compare_json_to_file(os.path.basename(file_info['full_filename']), f['name']):
                        # JSON matches to file - assign json contents as file meta info
                        f["info"].update(contents)
                        fw.set_acquisition_file_info(
                                ses_acq['_id'],
                                f['name'],
                                f['info'])

        # Figure out which acquisition files within ACQUISITION should have JSON info attached...
        elif (file_info['id_type'] == 'acquisition'):
            acq = fw.get_acquisition(file_info['_id'])
            for f in acq['files']:
                # Determine if json file components are all within the acq filename
                if compare_json_to_file(os.path.basename(file_info['full_filename']), f['name']):
                    # JSON matches to file - assign json contents as file meta info
                    f["info"].update(contents)
                    fw.set_acquisition_file_info(
                            acq['_id'],
                            f['name'],
                            f['info'])

def convert_dtype(contents):
    """
    Take the parsed TSV file and convert columns
        from string to float or int
    """
    # Convert contents to array
    contents_arr = contents[1:]
    cols = list(zip(*contents_arr))

    # Iterate over every column in array
    for idx in range(len(cols)):
        # Get column
        col = cols[idx]

        # Determine if column contains float/integer/string
        #    Check if first element is a float
        if '.' in col[0]:
            # Try to convert to float
            try:
                col = [float(x) for x in col]
            except ValueError:
                pass
        # Else try and convert column to integer
        else:
            # Convert to integer
            try:
                col = [int(x) for x in col]
            # Otherwise leave as string
            except ValueError:
                pass

        # Check if column only contains 'F'/'M'
        #   if so, convert to 'Female'/'Male'
        if set(col).issubset({'F', 'M', 'O'}):
            # Iterate over column, replace
            col = list(col)
            for idxxx, item in enumerate(col):
                if item == 'F':
                    col[idxxx] = 'female'
                elif item == 'M':
                    col[idxxx] = 'male'
                elif item == 'O':
                    col[idxxx] = 'other'
                else:
                    continue
        ### Take converted column and place back into the content list
        for idxx in range(len(contents[1:])):
            contents[idxx+1][idx] = col[idxx]

    return contents

def parse_tsv(filename):
    """"""
    contents = []
    with open(filename) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            contents.append(row)

    # If all values in the column are floats/ints, then convert
    # If only 'F' and 'M' in a column, convert to 'Female'/'Male'
    contents = convert_dtype(contents)

    return contents

def attach_tsv(fw, file_info):
    ## Parse TSV file
    contents = parse_tsv(file_info['full_filename'])

    ## Attach TSV file contents
    #Get headers of the TSV file
    headers = contents[0]
    tsvdata = contents[1:]
    # Define keys for the info dict
    keys = headers[1:]

    # Get all sessions within project_id
    if file_info['id_type'] == 'project':
        # Get sessions within project
        sessions = fw.get_project_sessions(file_info['_id'])
        # Iterate over sessions
        for ses in sessions:
            # Iterate over all values within TSV -- see if it matches
            for row in tsvdata:
                # Get values for the specific subject
                values = row[1:]
                # Create dict
                info_object = dict(zip(keys, values))
                # If it is a session label
                if row[0] == ses['label']:
                    session_info = {'info': info_object}
                # If it is a subject code
                elif row[0] == ses['subject']['code']:
                    session_info = {'subject': {'info': {}}}
                    # Iterate over subject info object
                    #   if a known field, (age, sex, etc) do not place in 'info' object
                    for key in info_object:
                        # If key is age, convert from years to seconds
                        if key == 'age':
                            session_info['subject'][key] = int(info_object[key] * 31536000)
                        elif key in ['first name', 'last name', 'sex', 'race', 'ethnicity']:
                            session_info['subject'][key] = info_object[key]
                        else:
                            session_info['subject']['info'][key] = info_object[key]
                else:
                    continue
                # Modify session
                fw.modify_session(ses['_id'], session_info)

    # Else id_type is 'session' and we get acquisitions
    else:
        # Get all acquisitions within session
        acquisitions = fw.get_session_acquisitions(file_info['_id'])
        # Iterate over all acquisitions within session
        for acq in acquisitions:
            # Get files within acquisitions
            for f in acq['files']:
                # Iterate over all values within TSV -- see if it matches the file
                for row in tsvdata:
                    # Get filename from within tsv
                    #     format is 'func/<filename>'
                    filename = row[0].split('/')[-1]

                    # If file in acquisiton matches file in TSV file, add file info
                    if filename == f['name']:
                        # Get values for the specific subject
                        values = row[1:]
                        # Create dict
                        info_object = dict(zip(keys, values))
                        # Modify acquisition file
                        fw.set_acquisition_file_info(acq['_id'], filename, info_object)

def parse_meta_files(fw, files_of_interest):
    """

    i.e.

    files_of_interest = {
        'dataset_description.json': {
            '_id': u'5a1364af9b89b7001d1f357f',
            'id_type': 'project',
            'full_filename': '/7t_trt_reduced/dataset_description.json'
            },
        'participants.tsv': {
            '_id': u'5a1364af9b89b7001d1f357f',
            'id_type': 'project',
            'full_filename': '/7t_trt_reduced/participants.tsv'
            }
    }

    Interested in these files within the project:
        data_description.json
        participants.tsv
        sub-YYY_sessions.tsv
        sub-YYY_ses-YYY_scans.tsv

    """
    logger.info('Parsing meta files')

    # Handle files
    for f in files_of_interest:
        if '.tsv' in f:
            # Attach TSV file contents
            attach_tsv(fw, files_of_interest[f])
        elif '.json' in f:
            # Attach JSON file contents
            attach_json(fw, files_of_interest[f])
        # Otherwise don't recognize filetype
        else:
            logger.info('Do not recognize filetype')

def upload_bids(fw, bids_dir, group_id, project_label=None, hierarchy_type='Flywheel', validate=True):
    ### Prep
    # Check directory name - ensure it exists
    validate_dirname(bids_dir)

    ### Read in hierarchy & Validate as BIDS
    # parse BIDS dir
    bids_hierarchy = parse_bids_dir(bids_dir)
    # TODO: Determine if project label are present
    bids_hierarchy, rootdir = handle_project_label(bids_hierarchy, project_label, bids_dir)

    # Determine if hierarchy is valid BIDS
    if validate:
        utils.validate_bids(rootdir)

    ### Upload BIDS directory
    # upload bids dir (and get files of interest and project id)
    files_of_interest = upload_bids_dir(fw, bids_hierarchy, group_id, rootdir, hierarchy_type)

    # Parse the BIDS meta files
    #    data_description.json, participants.tsv, *_sessions.tsv, *_scans.tsv
    parse_meta_files(fw, files_of_interest)

def main():
    ### Read in arguments
    parser = argparse.ArgumentParser(description='BIDS Directory Upload')
    parser.add_argument('--bids-dir', dest='bids_dir', action='store',
            required=True, help='BIDS directory')
    parser.add_argument('--api-key', dest='api_key', action='store',
            required=True, help='API key')
    parser.add_argument('-g', dest='group_id', action='store',
            required=True, help='Group ID on Flywheel instance')
    parser.add_argument('-p', dest='project_label', action='store',
            required=False, default=None, help='Project Label on Flywheel instance')
    parser.add_argument('--type', dest='hierarchy_type', action='store',
            required=False, default='Flywheel', choices=['BIDS', 'Flywheel'],
            help="Hierarchy to load into, either 'BIDS' or 'Flywheel'")
    args = parser.parse_args()

    # Check API key - raises Error if key is invalid
    fw = flywheel.Flywheel(args.api_key)

    upload_bids(fw, args.bids_dir, args.group_id, project_label=args.project_label, hierarchy_type=args.hierarchy_type)

if __name__ == '__main__':
    main()

