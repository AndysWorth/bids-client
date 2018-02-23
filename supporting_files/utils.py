import logging
import re
import sys
import subprocess
import jsonschema
import collections

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('utils')

def validate_bids(dirname):
    """ """
    logger.info('Validating BIDS directory')

    cmd = ['/usr/bin/bids-validator', dirname]
    proc = subprocess.Popen(cmd,
                            #cwd=dirname,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    returncode = proc.returncode

    # TODO: Determine if an error should be raised or just a warning
    logger.info('returncode: %d' % returncode)
    logger.info('stderr: ' + stderr)
    logger.info('stdout: ' + stdout)

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

def get_project_id_from_session_id(fw, session_id):
    """ """
    # Find project id from session
    session = fw.get_session(session_id)
    if not session:
        logger.error('Could not load session %s.' % session_id)
        sys.exit(1)

    return session['project']


def get_extension(fname):
    """ Get extension

    If search returns a result, get value
    else, ext is None

    """
    ext = re.search('\.[a-zA-Z]*[\.]?[A-Za-z0-9]+$',fname)
    if ext:
        ext = ext.group()
    return ext

def dict_lookup(obj, value):
    # For now, we don't support escaping of dots
    parts = value.split('.')
    curr = obj
    for part in parts:
        if isinstance(curr, (dict, collections.Mapping)) and part in curr:
            curr = curr[part]
        elif isinstance(curr, list) and int(part) < len(curr):
            curr = curr[int(part)]
        else:
            curr = None
            break
    return curr

def normalize_strings(obj):
    if isinstance(obj, basestring):
        return str(obj)
    if isinstance(obj, collections.Mapping):
        return dict(map(normalize_strings, obj.iteritems()))
    if isinstance(obj, collections.Iterable):
        return type(obj)(map(normalize_strings, obj))
    return obj


