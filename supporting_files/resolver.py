import re
import utils

class Filter:
    def __init__(self, fields):
        self.fields = fields

    def test(self, context):
        for prop, filter_value in self.fields.items():
            prop_val = utils.dict_lookup(context, prop)
            if isinstance(filter_value, list):
                if prop_val not in filter_value:
                    return False
            else:
                if prop_val != filter_value:
                    return False
        return True


class Resolver:
    def __init__(self, namespace, resolverDef): 
        self.namespace = namespace
        self.id = resolverDef.get('id')
        self.templates = resolverDef.get('templates', [])
        self.update_field = resolverDef.get('update')
        self.filter_field = resolverDef.get('filter')
        self.container_type = resolverDef.get('type')
        self.format = resolverDef.get('format')

    def resolve(self, session, context):
        results = []

        # Determine filter fields, and add namespace prefix for matching
        filter_fields = utils.dict_lookup(context, self.filter_field, {})
        fields = {}
        if self.container_type:
            fields['container_type'] = self.container_type
        for k, v in filter_fields.items():
            key = '{}.info.{}.{}'.format(self.container_type, self.namespace, k)
            fields[key] = v
        filt = Filter(fields)

        # Iterate through the contexts in the session, collecting matches
        for ctx in session.context_iter():
            if filt.test(ctx):
                results.append(utils.process_string_template(self.format, ctx))
        
        # Finally update the field specified
        utils.dict_set(context, self.update_field, results)


    

    
