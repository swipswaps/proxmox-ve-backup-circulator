#!/usr/bin/env python
# @author    Andreas Fischer <af@bantuX.org>
# @copyright 2014 Andreas Fischer
# @license   http://www.opensource.org/licenses/mit-license.html MIT License

import os
import subprocess
import sys

def shell(cmd):
    """
    Executes a list as a shell command and returns the result as a list of
    lines.
    """
    return subprocess.check_output(cmd).strip().split("\n")

def get_node_status():
    """
    Returns the output of 'pvecm status' as a dictionary.
    """
    return dict(
        map(lambda s: s.strip(), line.split(':'))
        for line in shell(['pvecm', 'status'])
    )

def get_node_id_to_name_map():
    """
    Returns the output 'pvecm nodes' as a dictionary.
    """
    def f(line):
        split = line.strip().split(' ')
        return [int(split.pop(0)), split.pop()]
    lines = shell(['pvecm', 'nodes'])
    lines.pop(0)
    return dict(map(f, lines))

def get_ct_vm_ids(cmd):
    """
    Takes a command as a list and executes it. From the output, the first line
    is thrown away. Then the first column is returned as a list of integers.
    """
    lines = shell(cmd)
    lines.pop(0)
    return map(lambda l: int(l.strip().split(' ').pop(0)), lines)

def get_container_ids():
    """
    Returns a list of OpenVZ container IDs hosted on this node.
    """
    return get_ct_vm_ids(['vzlist'])

def get_vm_ids():
    """
    Returns a list of VM IDs hosted on this node.
    """
    return get_ct_vm_ids(['qm', 'list'])

def main(args):
    # Get data of current node
    my_node_id = int(get_node_status()['Node ID'])

    # Get map from node id to node name
    node_id_to_name_map = get_node_id_to_name_map()

    # Get sorted list of node ids
    node_list = node_id_to_name_map.keys()
    node_list.sort()

    # Get the next node list index, add 1, translate to name.
    next_node_index = node_list.index(my_node_id) + 1
    next_node_id = node_list[next_node_index % len(node_list)]
    next_node_name = node_id_to_name_map[next_node_id]

    # Get prefixes and suffixes of filename we have to look for.
    prefixes = tuple(
        map(lambda i: 'vzdump-openvz-%d-' % i, get_container_ids()) +
        map(lambda i: 'vzdump-qemu-%d-' % i, get_vm_ids())
    )
    extensions = ('.log', '.tar.gz', '.tar.lzo', '.vma.gz', '.vma.lzo')

    # Do the actual file moving
    dir = '/var/lib/vz/dump'
    for filename in os.listdir(dir):
        if filename.endswith(extensions) and filename.startswith(prefixes):
            shell([
                'rsync',
                '--times', '--perms', '--partial', '--remove-source-files',
                '%s/%s' % (dir, filename),
                '%s:%s/%s' % (next_node_name, dir, filename)
            ])

if __name__ == '__main__':
    main(sys.argv[1:])
