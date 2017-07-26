__author__ = 'lijuk'

import os
import glob

root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
NODE_PATH = os.path.join(root, "nodes")


def get_node_list():
    """
    Gather all node modules from node path
    :return: dict
    """
    path_glob = "{0}/*_node.py".format(NODE_PATH)
    node_modules = glob.glob(path_glob)
    node_dict = dict()
    for each_module in node_modules:
        node_name = os.path.basename(each_module)[:-2].split("_node")[0]
        node_dict[node_name] = each_module
    return node_dict
