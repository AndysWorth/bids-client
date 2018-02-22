import collections
import logging
import copy
from supporting_files import utils
logger = logging.getLogger('curate-bids')

class TreeNode(collections.MutableMapping):
    def __init__(self, node_type, data):
        self.type = node_type
        self.data = data
        self.children = []
   
        # save a copy of original info object so we know when
        # we need to do an update
        self.original_info = copy.deepcopy(self.data.get('info'))

    def is_dirty(self):
        info = self.data.get('info')
        return info != self.original_info

    def context_iter(self, context=None):
        if not context:
            context = {'parent_container_type': None}

        # Depth-first walk down tree
        context['container_type'] = self.type
        context[self.type] = self
        
        # Bring subject to top-level of context
        if self.type == 'session':
            context['subject'] = self.data['subject']

        # Additionally bring ext up if file
        if self.type == 'file':
            context['ext'] = utils.get_extension(self.data['name'])

        # Yield the current context before processing children
        yield context

        for child in self.children:
            context['parent_container_type'] = self.type
            for ctx in child.context_iter(context):
                yield ctx

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)
    
    def __contains__(self, key):
        return key in self.data

    def __repr__(self):
        return repr(self.data)

def add_file_nodes(parent):
    for f in parent.get('files', []):
        parent.children.append(TreeNode('file', f))

def get_project_tree(fw, project_id):
    """
    fw: Flywheel client
    project_id: project id of project to curate
    """
    # Get project
    logger.info('Getting project...')
    project_data = fw.get_project(project_id)
    project_node = TreeNode('project', project_data)
    add_file_nodes(project_node)

    # Get project sessions
    project_sessions = fw.get_project_sessions(project_id)
    for proj_ses in project_sessions:
        session_data = fw.get_session(proj_ses['_id'])
        session_node = TreeNode('session', session_data)
        add_file_nodes(session_node)

        project_node.children.append(session_node)

        # Get acquisitions within session
        session_acqs = fw.get_session_acquisitions(proj_ses['_id'])
        for ses_acq in session_acqs:
            # Get true acquisition, in order to access file info
            acquisition_data = fw.get_acquisition(ses_acq['_id'])
            acquisition_node = TreeNode('acquisition', acquisition_data)
            add_file_nodes(acquisition_node)

            session_node.children.append(acquisition_node)

    return project_node

