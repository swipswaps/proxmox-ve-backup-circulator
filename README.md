# circulate-backup.py

Treats nodes of a [Proxmox VE](https://pve.proxmox.com) cluster as a ring
identified by their node id and moves backup files to the successor node
using rsync.

## Usage

Calling `circulate-backup.py` will move any backup files of VMs and CTs hosted
on the current node to the successor node. Any other backup files will be kept.

Tip:
If the number of nodes in the cluster is odd, it might make sense to run this
in a one node at a time fashion.

Tip:
If the number of nodes in the cluster is even, it might make sense to first
call `circulate-backup.py` on all nodes with an even node id, followed by
the other half.
