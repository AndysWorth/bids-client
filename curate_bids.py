import argparse
import logging

import flywheel

from supporting_files import bidsify_flywheel, utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('curate-bids')

def update_meta_info(fw, context):
    """ Update file information

    """
    # Modify file
    if context['container_type'] == 'file':
        # Modify acquisition file
        if context['parent_container_type'] == 'acquisition':
            fw.set_acquisition_file_info(
                    context['acquisition']['_id'],
                    context['file']['name'],
                    context['file']['info']
                    )
        # Modify project file
        elif context['parent_container_type'] == 'project':
            fw.set_project_file_info(
                    context['project']['_id'],
                    context['file']['name'],
                    context['file']['info']
                    )
        # Modify session file
        elif context['parent_container_type'] == 'session':
            fw.set_session_file_info(
                    context['session']['_id'],
                    context['file']['name'],
                    context['file']['info']
                    )
        else:
            logger.info('Cannot determine file parent container type')
    # Modify project
    elif context['container_type'] == 'project':
        fw.modify_project(
                context['project']['_id'],
                {'info': context['project']['info']}
                )
    # Cannot determine container type
    else:
        logger.info('Cannot determine container type')

def curate_bids_dir(fw, project_id):
    """

    fw: Flywheel client
    project_id: project id of project to curate

    """
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

    # Get project
    logger.info('Getting project...')
    context['project'] = fw.get_project(project_id)

    # Curate Project
    context['container_type'] = 'project'
    bidsify_flywheel.process_matching_templates(context)
    # Update project meta information
    update_meta_info(fw, context)

    # Iterate over all files within project
    logger.info('Updating project files...')
    for f in context['project'].get('files', []):
        # Update the context for this file
        context['file'] = f
        context['container_type'] = 'file'
        context['parent_container_type'] = 'project'
        context['ext'] = utils.get_extension(f['name'])
        # Identify the templates for the file and return file object
        context['file'] = bidsify_flywheel.process_matching_templates(context)
        # Update file meta information
        update_meta_info(fw, context)

    # Iterate over all files within session
    logger.info('Updating session files...')
    # Get project sessions
    project_sessions = fw.get_project_sessions(project_id)
    for proj_ses in project_sessions:
        # Get true session, in order to access file info
        context['session'] = fw.get_session(proj_ses['_id'])
        context['subject'] = context['session']['subject']
        # Iterate over any session files
        for f in context['session'].get('files', []):
            # Update the context for this file
            context['file'] = f
            context['container_type'] = 'file'
            context['parent_container_type'] = 'session'
            context['ext'] = utils.get_extension(f['name'])
            # Identify the templates for the file and return file object
            context['file'] = bidsify_flywheel.process_matching_templates(context)
            # Update file meta information
            update_meta_info(fw, context)

        # Iterate over all files within acquisition
        logger.info('Updating acquisition files...')
        # Get acquisitions within session
        session_acqs = fw.get_session_acquisitions(context['session']['_id'])
        for ses_acq in session_acqs:
            # Get true acquisition, in order to access file info
            context['acquisition'] = fw.get_acquisition(ses_acq['_id'])
            # Iterate over acquistion files
            for f in context['acquisition'].get('files', []):
                # Update the context for this file
                context['file'] = f
                context['container_type'] = 'file'
                context['parent_container_type'] = 'acquisition'
                context['ext'] = utils.get_extension(f['name'])
                # Identify the templates for the file and return file object
                context['file'] = bidsify_flywheel.process_matching_templates(context)
                # Update file meta info
                update_meta_info(fw, context)

if __name__ == '__main__':
    ### Read in arguments
    parser = argparse.ArgumentParser(description='BIDS Curation')
    parser.add_argument('--api-key', dest='api_key', action='store',
            required=True, help='API key')
    parser.add_argument('-p', dest='project_label', action='store',
            required=False, default=None, help='Project Label on Flywheel instance')
    args = parser.parse_args()

    ### Prep
    # Check API key - raises Error if key is invalid
    fw = flywheel.Flywheel(args.api_key)
    # Get project id from label
    project_id = utils.validate_project_label(fw, args.project_label)

    ### Curate BIDS project
    curate_bids_dir(fw, project_id)
