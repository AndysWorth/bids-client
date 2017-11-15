import json
import jsonschema
import pprint
import re

import flywheel

import templates

# get project by label
def get_project_by_label(client, label):
    projects = client.get_all_projects()
    project = [project for project in projects if project['label'] == label]
    return(project)

# validate namespace template against the template schema
def valid_namespace(namespace):
    """ Validate the namespace

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
    jsonschema.validate(namespace,template_schema)

# process_string_template(template, context)
# finds values in the context object and substitutes them into the string template
# Use <path> for cases where you want the result converted to lowerCamelCase
# Use {path} for cases where you want a literal value substitution
# path uses dot notation to navigate the context for desired values
# path examples:  <session.label>  returns session.label in lowercamelcase
#                 {file.info.BIDS.Filename} returns the value of file.info.BIDS.Filename
#                 {file.info.BIDS.Modality} returns Modality without modification
# example template string:
#       'sub-<subject.code>_ses-<session.label>_acq-<acquisition.label>_{file.info.BIDS.Modality}.nii.gz'

def process_string_template(template, context):
    tokens = re.compile('[^\[][A-Za-z0-9\.><}{-]+|\[[A-Za-z0-9><}{_\.-]+\]')
    values = re.compile('[{<][A-Za-z0-9\.-]+[>}]')
    translated_tokens = []
    for token in tokens.findall(template):
        #
        # improve this to handle multiple value tokens in the same token (ie. modality type and ext)
        #
        if values.search(token):
            replace_token = values.search(token).group()
            path = replace_token[1:len(values.search(token).group())-1]
            keys = path.split(".")
            result = context
            for key in keys:
                if key in result:
                    result = result[key]
                else:
                    result = None
                    break
            if result:
                if replace_token[0] == '<':
                    result = ''.join(x for x in result.replace('_', ' ').replace('-', ' ').title() if x.isalnum())
                    result = result[0].lower() + result[1:]
                translated_token = token.replace(replace_token, result).replace('[','').replace(']','')
                translated_tokens.append(translated_token)
            elif token[0] != '[':
                translated_tokens.append(token)
        else:
            translated_tokens.append(token)

    processed_template = ''.join(translated_tokens)
    return(processed_template)

# add_properties(properties, obj)
# Populates obj with properties defined in a namespace template
# Adds each key in the properties list and sets the value to the value specified in 'default' attribute
# Properties may be of type string or object. Will add other types later.

def add_properties(properties, obj):
    for key in properties:
        proptype = properties[key]["type"]
        if proptype == "string":
            if "default" in properties[key]:
                obj[key] = properties[key]["default"]
            else:
                obj[key] = "default"
        elif proptype == "object":
            obj[key] = {}
            obj[key] = add_properties(properties[key]["properties"], obj[key])
    return(obj)


# update_properties(properties, context, obj)
# Updates object values for items in properties list containing an 'auto_update' attribute.
# 'auto_update' may be specified using a string template containing tags to be replaced from value in 'context' object
# See process_string_template for details on how to use string templates
# Updated keys are added to the obj object for later update to Flywheel

def update_properties(properties, context, obj):
    for key in properties:
        proptype = properties[key]["type"]
        if proptype == "string":
            if "auto_update" in properties[key]:
                obj[key] = process_string_template(properties[key]['auto_update'],context)
        elif proptype == "object":
            obj[key] = {}
            obj[key] = update_properties(properties[key]["properties"], context, obj[key])
    return(obj)


# process_matching_templates(context)
# Accepts a context object that represents a Flywheel container and related parent containers
# and looks for matching templates in namespace.
# Matching templates define rules for adding objects to the container's info object if they don't already exist
# Matching templates with 'auto_update' rules will update existing info object values each time it is run.

def process_matching_templates(context):
    container_type = context['container_type']
    container = context[container_type]
    # add objects based on template if they don't already exist
    if ("info" in container and templates.namespace["namespace"] not in container["info"]) or "info" not in container:
        for template in templates.namespace["datatypes"]:
            if ((template["container_type"] == context["container_type"] and 'parent_container_type' not in template)
                or
                ('parent_container_type' in template and template["container_type"] == context["container_type"] and
                 template['parent_container_type'] == context['parent_container_type'])):
                match = True
                if "where" in template:
                    for key in template["where"]:
                        if key in container:
                            match = template["where"][key] == container[key]
                            if match == False:
                                break
                        else:
                            match = False
                            break
                if match == True:
                    print("matches template=", template["description"])
                    obj = {}
                    namespacekey = templates.namespace["namespace"]
                    if "info" not in container:
                        container["info"] = {}
                    if namespacekey not in container["info"]:
                        container["info"][namespacekey] = {}
                    else:
                        obj = container["info"][namespacekey]
                    obj = add_properties(template["properties"], obj)
                    container["info"][namespacekey] = obj

    # update info object values for matching templates that contain 'auto_update' rules
    if ("info" in container and templates.namespace["namespace"] in container["info"]):
        for template in templates.namespace["datatypes"]:
            if ((template["container_type"] == context["container_type"] and 'parent_container_type' not in template)
                or
                ('parent_container_type' in template and template["container_type"] == context["container_type"] and
                 template['parent_container_type'] == context['parent_container_type'])):
                match = True
                if "where" in template:
                    for key in template["where"]:
                        if key in container:
                            match = template["where"][key] == container[key]
                            if match == False:
                                break
                        else:
                            match = False
                            break
                if match == True:
                    print("matches template=", template["description"])
                    obj = {}
                    namespacekey = templates.namespace["namespace"]
                    obj = update_properties(template["properties"], context, obj)
                    # Update container with auto-updated values
                    container["info"][namespacekey].update(obj)
                    print('updated info.namespace properties:', obj)
                    print('\n')

    return container

# apply_namespace_templates(project)

def apply_namespace_templates(project):

    # initialize context object
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

    # Validate the namespace and related templates
    valid_namespace(templates.namespace)

    # process project
    print(project["label"])
    context['container_type'] = 'project'
    context['project'] = project
    process_matching_templates(context)

    # process project files
    print("\tFiles:")
    if 'files' in project:
        for f in project["files"]:
            print("\t\t" + f["name"])
            context['parent_container_type'] = 'project'
            context['container_type'] = 'file'
            context['file'] = f
            context['ext'] = re.search('\.[A-Za-z0-9\._-]+',f['name']).group()
            process_matching_templates(context)

    # process project subjects
    # until we formalize subject, this section will group sessions by subject code
    print("\tSubjects:")
    sessions = fw.get_project_sessions(project["_id"])
    subjects = {}
    for session in sessions:
        subjects.setdefault(session["subject"]["code"], []).append(session)

    for subject_code in subjects:
        print("\t\t" + subject_code)
        context['container_type'] = 'subject'
        context['parent_container_type'] = 'project'
        context['subject'] = {'code': subject_code }
        context['session'] = None
        context['acquisition'] = None
        context['file'] = None
        context['ext'] = None
        process_matching_templates(context)

        # process subject sessions
        for session in subjects[subject_code]:
            print("\t\t\t" + session["label"])
            context['container_type'] = 'session'
            context['parent_container_type'] = 'subject'
            context['session'] = session
            context['acquisition'] = None
            context['file'] = None
            context['ext'] = None
            process_matching_templates(context)

            # process session files
            if 'files' in session:
                for f in session["files"]:
                    print("\t\t\t\t" + f["name"])
                    context['container_type'] = 'file'
                    context['parent_container_type'] = 'session'
                    context['file'] = f
                    context['ext'] = re.search('\.[A-Za-z0-9\._-]+',f['name']).group()
                    process_matching_templates(context)

            # process session acquisitions
            for acquisition in fw.get_session_acquisitions(session["_id"]):
                print("\t\t\t\t" + acquisition["label"])
                context['container_type'] = 'acquisition'
                context['parent_container_type'] = 'session'
                context['acquisition'] = acquisition
                context['file'] = None
                context['ext'] = None
                process_matching_templates(context)

                # process acquisition files
                if 'files' in acquisition:
                    for f in acquisition["files"]:
                        print("\t\t\t\t\t" + f["name"])
                        context['container_type'] = 'file'
                        context['parent_container_type'] = 'acquisition'
                        context['acquisition'] = acquisition
                        context['file'] = f
                        context['ext'] = re.search('\.[A-Za-z0-9\._-]+',f['name']).group()
                        process_matching_templates(context)
