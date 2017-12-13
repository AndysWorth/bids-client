import logging
import re
import subprocess
import jsonschema


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

def get_extension(fname):
    """ Get extension

    If search returns a result, get value
    else, ext is None

    """
    ext = re.search('\.[A-Za-z0-9\._-]+',fname)
    if ext:
        ext = ext.group()
    return ext

def valid_namespace(namespace):
    """ Validate the namespace against the template schema

    To use...
        import templates
        valid_namespace(templates.namespace)

    If namespace is not valid, a jsonschema.ValidationError will be raised,
        otherwise, no error raised

    """
    template_schema = {
        "type": "object",
        "properties": {
            "namespace": {"type": "string"},
            "description": {"type": "string"},
            "datatypes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "description": "string",
                    "properties": {
                        "container_type": {"type": "string"},
                        "parent_container_type": {"type": "string"},
                        "where": {"type": "object"},
                        "properties": {"type": "object"},
                        "required": {"type": "array"}
                    },
                    "required": ["container_type","properties"]
                }
            }
        },
        "required": ["namespace"]
    }
    jsonschema.validate(namespace, template_schema)

