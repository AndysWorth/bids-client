import os, os.path, json, re
import utils

DEFAULT_TEMPLATE_NAME = 'bids-v1'
BIDS_TEMPLATE_NAME = 'bids-v1'
DEFAULT_TEMPLATES = {}

class Template:
    """
    Represents a project-level template for organizing data.

    Args:
        data (dict): The json configuration for the template
        templates (list): The optional existing map of templates by name.

    Attributes:
        namespace (str): The namespace where resolved template data is displayed.
        description (str): The optional description of the template.
        definitions (dict): The map of template definitions.
        rules (list): The list of if rules for applying templates.
        extends (string): The optional name of the template to extend.
        exclude_rules (list): The optional list of rules to exclude from a parent template.
    """
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
        """
        Implements the extends logic for this template.

        Args:
            templates (list): The existing list of templates.
        """
        if not self.extends:
            return

        if self.extends not in templates:
            raise Exception('Could not find parent template: {0}'.format(self.extends))

        parent = templates[self.extends]

        if not self.namespace:
            self.namespace = parent.namespace

        my_rules = self.rules
        my_defs = self.definitions

        # Extend definitions
        self.definitions = parent.definitions.copy()
        for key, value in my_defs.items():
            self.definitions[key] = value

        # Extend rules, after filtering excluded rules
        filtered_rules = filter(lambda x: x.id not in self.exclude_rules, parent.rules)
        self.rules = list(filtered_rules) + my_rules

    def compile_rules(self):
        """
        Converts the rule dictionaries on this object to Rule class objects.
        """
        for i in range(0, len(self.rules)):
            rule = self.rules[i]
            if not isinstance(rule, Rule):
                self.rules[i] = Rule(rule)

class Rule:
    """
    Represents a matching rule for applying template definitions to resources or files within a project.

    Args:
        data (dict): The rule definition as a dictionary.

    Attributes:
        id (string): The optional rule id.
        template (str): The name of the template id to apply when this rule matches.
        initialize (dict): The optional set of initialization rules when this rule matches.
        conditions (dict): The set of conditions that must be true for this rule to match.
    """
    def __init__(self, data):
        self.id = data.get('id', '')
        self.template = data.get('template')
        self.initialize = data.get('initialize', {})
        if self.template is None:
            raise Exception('"template" field is required!')
        self.conditions = data.get('where')
        if not self.conditions:
            raise Exception('"where" field is required!')

    def test(self, context):
        """
        Test if the given context matches this rule.
        
        Args:
            context (dict): The context, which includes the hierarchy and current container

        Returns:
            bool: True if the rule matches the given context.
        """
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

    def initializeProperties(self, info, context):
        """
        Attempts to resolve initial values of BIDS fields from context.

        Template properties can now include an "initialize" field that gives instructions on how to attempt to
        initialize a field based on context. Within the initialize object, there are a list of keys to extract
        from the context, and currently regular expressions to match against the extracted fields. If the regex
        matches, then the "value" group will be extracted and assigned. Otherwise if 'take' is True for an initialization
        spec, we will copy that value into the field.

        Args:
            context (dict): The full context object
            info (dict): The BIDS data to update, if matched
        """
        for propName, propDef in self.initialize.items():
            resolvedValue = None

            if isinstance(propDef, dict):
                for key, valueSpec in propDef.items():
                    # Lookup the value of the key
                    value = utils.dict_lookup(context, key)
                    if value is not None:
                        # Regex matching must provide a 'value' group
                        if '$regex' in valueSpec:
                            m = re.search(valueSpec['$regex'], value)
                            if m is not None:
                                resolvedValue = m.group('value')
                        # 'take' will just copy the value
                        elif '$take' in valueSpec and valueSpec['$take']:
                            resolvedValue = value

                        if resolvedValue:
                            break
            else:
                resolvedValue = propDef

            if resolvedValue:
                info[propName] = resolvedValue


def processValueMatch(value, match):
    """
    Helper function that recursively performs value matching.
    Args:
        value: The value to match
        match: The matching rule
    Returns:
        bool: The result of matching the value against the match spec.
    """
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

        elif '$regex' in match:
            regex = re.compile(match['$regex'])

            if isinstance(value, list):
                for item in value:
                    if regex.search(item) is not None:
                        return True

                return False
            
            return regex.search(value) is not None 

    else:
        # Direct match
        if isinstance(value, list):
            for item in value:
                if item == match:
                    return True
            return False

        return value == match

def loadTemplates(templates_dir=None):
    """
    Load all templates in the given (or default) directory
    
    Args:
        templates_dir (string): The optional directory to load templates from.
    """
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

def loadTemplate(path, templates=None):
    """
    Load the template at path
    
    Args:
        path (str): The path to the template to load
        templates (dict): The mapping of template names to template defintions.
    Returns:
        Template: The template that was loaded (otherwise throws)
    """
    with open(path, 'r') as f:
        data = json.load(f)

    if templates is None:
        templates = DEFAULT_TEMPLATES

    return Template(data, templates)

DEFAULT_TEMPLATES = loadTemplates()
DEFAULT_TEMPLATE = DEFAULT_TEMPLATES.get(DEFAULT_TEMPLATE_NAME)
BIDS_TEMPLATE = DEFAULT_TEMPLATES.get(BIDS_TEMPLATE_NAME)

