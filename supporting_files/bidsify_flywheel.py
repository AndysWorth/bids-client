import json
import pprint
import re

import flywheel

from supporting_files import classifications
import templates
import utils

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
    tokens = re.compile('[^\[][A-Za-z0-9\.><}{-]+|\[[/A-Za-z0-9><}{_\.-]+\]')
    values = re.compile('[{<][A-Za-z0-9\.-]+[>}]')

    for token in tokens.findall(template):
        if values.search(token):
            replace_tokens = values.findall(token)
            for replace_token in replace_tokens:
                # Remove the {} or <> surrounding the replace_token
                path = replace_token[1:-1]
                # Get keys, if replace token has a . in it
                keys = path.split(".")
                result = context
                for key in keys:
                    if key in result:
                        result = result[key]
                    else:
                        result = None
                        break
                # If value found replace it
                if result:
                    # If replace token is <>, need to check if in BIDS
                    if replace_token[0] == '<':
                        # Check if result is already in BIDS format...
                        #   if so, split and grab only the label
                        if re.match('(sub|ses)-[a-zA-Z0-9]+', result):
                            label, result = result.split('-')
                        # If not, take the entire result and remove underscores and dashes
                        else:
                            result = ''.join(x for x in result.replace('_', ' ').replace('-', ' ').title() if x.isalnum())
                            result = result[0].lower() + result[1:]

                    # Replace the token with the result
                    template = template.replace(replace_token, result)
                # If result not found, but the token is option, remove the token from the template
                elif token[0] == '[':
                    template = template.replace(token, '')

                # TODO: Determine approach
                # Else the value hasn't been found AND field is required, and so let's replace with 'UNKNOWN'
                #elif token[0] != '[':
                #    result = 'UNKNOWN'
                #    template = template.replace(replace_token, result)
        else:
            pass

    # Replace any [] from the string
    processed_template = re.sub('\[|\]', '', template)

    return processed_template


def determine_enum(theproperty, key, measurements):
    """

    obj:  {'Task': '', 'Run': '', 'Filename': '', 'Acq': '', 'Rec': '', 'Path': '', 'Folder': 'func', 'Echo': ''}
    property: {'default': 'bold', 'enum': ['bold', 'sbref', 'stim', 'physio'], 'type': 'string', 'label': 'Modality Label'}
    measurements:  [u'functional']

    """
    # Use the default value
    enum_value = theproperty.get('default', '')
    # If the default value is '', try and determine if from 'enum' list
    if not enum_value:
        # If key is modality, iterate over classifications dict
        if key == 'Modality':
            for k1 in classifications.classifications:
                for k2 in classifications.classifications[k1]:
                    if measurements[0] == classifications.classifications[k1][k2]:
                        enum_value = k2
                        break

    return enum_value

# add_properties(properties, obj, measurements)
# Populates obj with properties defined in a namespace template
# Adds each key in the properties list and sets the value to the value specified in 'default' attribute
# Properties may be of type string or object. Will add other types later.
# Measurements passed through function so that Modality value can be determined

def add_properties(properties, obj, measurements):
    for key in properties:
        proptype = properties[key]["type"]
        if proptype == "string":
            # If 'enum' in properties, seek to determine the value from enum list
            if "enum" in properties[key]:
                obj[key] = determine_enum(properties[key], key, measurements)
            elif "default" in properties[key]:
                obj[key] = properties[key]["default"]
            else:
                obj[key] = "default"
        elif proptype == "object":
            print 'WHY AM I HERE?!?'
            obj[key] = {}
            obj[key] = add_properties(properties[key]["properties"], obj[key], measurements)
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

def process_matching_templates(context, template=templates.DEFAULT_TEMPLATE):
    namespace = template.namespace

    container_type = context['container_type']
    container = context[container_type]

    initial = (('info' not in container) or (namespace not in container['info']) 
            or ('template' not in container['info'][namespace]))

    templateDef = None

    # add objects based on template if they don't already exist
    if initial:
        # Do initial rule matching
        for rule in template.rules:
            if rule.test(context):
                print 'matches template={0}'.format(rule.template)
                templateDef = template.definitions.get(rule.template)
                if templateDef is None:
                    raise Exception('Unknown template: {0}'.format(rule.template))

                if 'info' not in container:
                    container['info'] = {}

                obj = container['info'].get(namespace, {})
                container['info'][namespace] = add_properties(templateDef['properties'], obj, container.get('measurements'))
                obj['template'] = rule.template
                rule.initializeProperties(obj, context)
                initial = False
                break

    if not initial:
        # Do auto_updates
        if not templateDef:
            templateDef = template.definitions.get(container['info'][template.namespace]['template'])
        data = update_properties(templateDef["properties"], context, {})
        container['info'][namespace].update(data)

    return container

