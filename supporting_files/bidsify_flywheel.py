import json
import pprint
import re

import flywheel

from supporting_files import classifications
import templates
import utils


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
            obj[key] = properties[key].get('default', {})
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
                obj[key] = utils.process_string_template(properties[key]['auto_update'],context)
    return(obj)


# process_matching_templates(context, template)
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
        match = False
        for rule in template.rules:
            if rule.test(context):
                print 'matches template={0}'.format(rule.template)
                match = True
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
        if not match:
            print 'no template matched for {} in {} {}'.format(container['name'], context['parent_container_type'], context[context['parent_container_type']]['_id'])

    if not initial:
        # Do auto_updates
        if not templateDef:
            templateDef = template.definitions.get(container['info'][template.namespace]['template'])
        if templateDef:
            data = update_properties(templateDef["properties"], context, {})
            container['info'][namespace].update(data)

    return container

def process_resolvers(session, context, template=templates.DEFAULT_TEMPLATE):
    """
    Perform second stage path resolution based on template rules

    Args:
        session (TreeNode): The session node to search within
        context (dict): The context to perform path resolution on
        template (Template): The template
    """
    namespace = template.namespace

    container_type = context['container_type']
    container = context[container_type]

    if (('info' not in container) or (namespace not in container['info']) or ('template' not in container['info'][namespace])):
        return
    
    # Determine the applied template name
    template_name = container['info'][namespace]['template']
    # Get a list of resolvers that apply to this template
    resolvers = template.resolver_map.get(template_name, [])

    # Apply each resolver
    for resolver in resolvers:
        resolver.resolve(session, context)


def ensure_info_exists(context, template=templates.DEFAULT_TEMPLATE):
    """
    Ensure that the given info object has an entry for the template namespace.

    Args:
        context (dict): The context that should have a valid info object
        template (Template): The template

    Returns:
        bool: Whether or not the info was updated.
    """
    updated = False
    if 'info' not in context:
        context['info'] = {}
        updated = True
    if template.namespace not in context['info']:
        context['info'][template.namespace] = {}
        updated = True

    return updated

