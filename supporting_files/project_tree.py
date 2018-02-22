import collections
import logging
import copy
import dateutil.parser
from supporting_files import utils
logger = logging.getLogger('curate-bids')

class TreeNode(collections.MutableMapping):
    """
    Represents a single node (Project, Session, Acquisition or File) in
    the Flywheel hierarchy.

    Args:
        node_type (str): The type of node (lowercase)
        data (dict): The node data

    Attributes:
        type: The type of node
        data: The node data
        children: The children belonging to this node
        original_info: The original value of the 'info' property
    """
    def __init__(self, node_type, data):
        self.type = node_type
        self.data = data
        self.children = []
   
        # save a copy of original info object so we know when
        # we need to do an update
        self.original_info = copy.deepcopy(self.data.get('info'))

    def is_dirty(self):
        """
        Check if 'info' attribute has been modified.

        Returns:
            bool: True if info has been modified, False if it is unchanged
        """
        info = self.data.get('info')
        return info != self.original_info

    def context_iter(self, context=None):
        """
        Iterate the tree depth-first, producing a context for each node.

        Args:
            context (dict): The parent context object

        Yields:
            dict: The context object for this node
        """
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
    """
    Add file nodes as children to parent.

    Args:
        parent (TreeNode): The parent node
    """
    for f in parent.get('files', []):
        parent.children.append(TreeNode('file', f))

def get_project_tree(fw, project_id):
    """
    Construct a project tree from the given project_id.

    Args:
        fw: Flywheel client
        project_id (str): project id of project to curate

    Returns:
        TreeNode: The project (root) tree node
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

        # Prepare for sorting by converting timestamps to datetime
        for ses_acq in session_acqs:
            format_acquisition_timestamps(ses_acq)

        for ses_acq in sorted(session_acqs, compare_acquisitions):
            # Get true acquisition, in order to access file info
            acquisition_data = fw.get_acquisition(ses_acq['_id'])
            acquisition_node = TreeNode('acquisition', acquisition_data)
            add_file_nodes(acquisition_node)

            session_node.children.append(acquisition_node)

    return project_node

def format_acquisition_timestamps(acq):
    timestamp = acq.get('timestamp')
    if timestamp:
        acq['timestamp'] = dateutil.parser.parse(timestamp)
    acq['created'] = dateutil.parser.parse(acq['created'])

def compare_acquisitions(acq1, acq2):
    # Prefer timestamp over created
    ts1 = acq1.get('timestamp')
    ts2 = acq2.get('timestamp')
    if ts1 and ts2:
        return int((ts1 - ts2).total_seconds())
    return int((acq1['created'] - acq2['created']).total_seconds())

