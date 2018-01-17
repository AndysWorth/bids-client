import os, os.path, json
import utils

DEFAULT_TEMPLATE_NAME = 'bids-v1'
BIDS_TEMPLATE_NAME = 'bids-v1'

class Template:
    def __init__(self, data=None, templates=None):
        if data:
            self.namespace = data.get('namespace')
            self.description = data.get('description', '')
            self.definitions = data.get('definitions', {})
            self.rules = data.get('rules', {})
            
            self.extends = data.get('extends')
            self.exclude_rules = data.get('exclude_rules', [])
        else:
            self.namespace = ''
            self.description = ''
            self.definitions = {}
            self.rules = []

            self.extends = None
            self.exclude_rules = []

        if templates:
            self.do_extend(templates)

        self.compile_rules()

    def do_extend(self, templates):
        if not self.extends:
            return

        if self.extends not in templates:
            raise Exception('Could not find parent template: {0}'.format(self.extends))

        parent = templates[self.extends]
        my_rules = self.rules
        my_defs = self.definitions

        # Extend definitions
        self.definitions = parent.definitions.copy()
        for key, value in my_defs.items():
            self.definitions[key] = value

        # Extend rules, after filtering excluded rules
        filtered_rules = filter(lambda x: x.get('id') not in self.exclude_rules, parent.rules)
        self.rules = list(filtered_rules) + my_rules

    def compile_rules(self):
        for i in range(0, len(self.rules)):
            rule = self.rules[i]
            if not isinstance(rule, Rule):
                self.rules[i] = Rule(rule)

class Rule:
    def __init__(self, data):
        self.id = data.get('id')
        self.template = data.get('template')
        self.initialize = data.get('initialize', {})
        if self.template is None:
            raise Exception('"template" field is required!')
        self.conditions = data.get('where')
        if not self.conditions:
            raise Exception('"where" field is required!')

    def test(self, context):
        # Process matches
        conditions = self.conditions

        # Handle $or clauses at top-level
        if '$or' in conditions:
            for field, match in conditions['$or']:
                value = utils.dict_lookup(context, field)
                if processValueMatch(value, match):
                    return True
            return False

        # Otherwise AND clauses
        if '$and' in conditions:
            conditions = conditions['$and']

        for field, match in conditions.items():
            value = utils.dict_lookup(context, field)
            if not processValueMatch(value, match):
                return False

        return True

    # Attempts to resolve initial values of BIDS fields from context
    # template: The matched template
    # context: The full context object
    # info: The BIDS data to update, if matched
    # 
    # Template properties can now include an "initialize" field that gives instructions on how to attempt to
    # initialize a field based on context. Within the initialize object, there are a list of keys to extract
    # from the context, and currently regular expressions to match against the extracted fields. If the regex
    # matches, then the "value" group will be extracted and assigned. Otherwise if 'take' is True for an initialization
    # spec, we will copy that value into the field.
    def initializeProperties(self, info, context):
        for propName, propDef in self.initialize.items():
            resolvedValue = None
            for key, valueSpec in propDef.items():
                # Lookup the value of the key
                value = utils.dict_lookup(context, key)
                if value is not None:
                    # Regex matching must provide a 'value' group
                    if 'regex' in valueSpec:
                        m = re.search(valueSpec['regex'], value)
                        if m is not None:
                            resolvedValue = m.group('value')
                    # 'take' will just copy the value
                    elif 'take' in valueSpec and valueSpec['take']:
                        resolvedValue = value
                    if resolvedValue:
                        break

            if resolvedValue:
                info[propName] = resolvedValue


def processValueMatch(value, match):
    if isinstance(match, dict):
        # Deeper processing
        if '$in' in match:
            # Check if value is in list
            if isinstance(value, list):
                for item in value:
                    if item in match['$in']:
                        return True
                return False
            
            return value in match['$in']

        elif '$not' in match:
            # Negate result of nested match
            return not processMatch(value, match['$not'])
    else:
        # Direct match
        if isinstance(value, list):
            for item in value:
                if item == match:
                    return True
            return False

        return value == match

def loadTemplates(templates_dir=None):
    """Load all templates in the given (or default) directory"""
    results = {}

    if templates_dir is None:
        script_dir = os.path.dirname( os.path.realpath(__file__) )
        templates_dir = os.path.join(script_dir, '../templates')

    # Load all templates from the templates directory
    for fname in os.listdir(templates_dir):
        path = os.path.join(templates_dir, fname)
        name, ext = os.path.splitext(fname)
        if ext == '.json' and os.path.isfile(path):
            results[name] = loadTemplate(path)

    return results

def loadTemplate(path):
    """Load the template at path"""
    with open(path, 'r') as f:
        data = json.load(f)

    return Template(data)

DEFAULT_TEMPLATES = loadTemplates()
DEFAULT_TEMPLATE = DEFAULT_TEMPLATES.get(DEFAULT_TEMPLATE_NAME)
BIDS_TEMPLATE = DEFAULT_TEMPLATES.get(BIDS_TEMPLATE_NAME)



