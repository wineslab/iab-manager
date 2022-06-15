# iab-manager

`iab-manager` is a WIP command-line tool for the creation, management, reconfiguration and testing of IAB networks based on Openair Interface and reproduced on Colosseum. 

The tool is mainly written in Python and can be executed either on a remote machine or any of the reserved SRNs.
`iab-manager` makes use of `Fabric` to transparently and remotely run subprocesses on SRNs. 

A modified version of OAI's packet gateway is included as a git submodule. This version allows framed routing, which is required to forward traffic through GTP-tunnels when the destionation IP is different from the endpoint IP. This is currently achieved through cached kernel lookups. TODO: synchronize cache clearing with kernel routing tables changes. 

## Usage

### Entrypoint
The user should provide the entrypoint SRN hostname. Colosseum's SSH gateway `colosseum-gw` will be employed. The manager can run directly on a SRN, in that case the entrypoint is not required. 

### SRN and network roles
`iab-manager` will retrieve the reserved SRN list (currently by arp probes) and assign a network role to each. Network role templates are defined in `NetElements.NodeRoleSequences`.

Currently supported SNR roles (all extending `NetEl` class):
* Core
* Donor
* MT
* DU
* UE

An exception is thrown if any SNR does not support the assigned network role. Network role support is determined by reading SNR capabilities saved in `/snr_type`. An exception is thrown if the file is not present.

The tool is ready to use after SNR discovery, connection and network role assignment is successfully completed

### Commands (TODO)

```
list {SRN | du | mt | ue | iab-node}

core {start | stop | status}

donor {start | stop | status}

du {id} {start | stop | status}

mt {id} {start | stop | status}

ue {id} {start | stop | status}

iab-node {add | del | status} {{du_id} {mt_id} | iab_id}

test {connectivity | latency | tp} {up | down} {du | mt | ue} {id} {args}

rf-scenario {start | stop} {id}
```
