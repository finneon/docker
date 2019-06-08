#!/usr/bin/env python
""" Remove IMM configuration of scaled-in nodes
    Overwritten from https://sourceforge.net/projects/opensaf/
    at opensaf-code/python/samples/scale_opensaf
"""
from __future__ import print_function
import re
import hashlib
import time
import argparse
import os
import subprocess

from pyosaf.utils.immom.accessor import ImmOmAccessor
from pyosaf.utils.immom.ccb import Ccb
from pyosaf.utils.immom.iterator import InstanceIterator as inst_iter
from pyosaf.saAmf import eSaAmfRedundancyModelT, eSaAmfAdminOperationIdT


TWO_N = eSaAmfRedundancyModelT.SA_AMF_2N_REDUNDANCY_MODEL
NWAYACTIVE = eSaAmfRedundancyModelT.SA_AMF_N_WAY_ACTIVE_REDUNDANCY_MODEL
NORED = eSaAmfRedundancyModelT.SA_AMF_NO_REDUNDANCY_MODEL
ADMIN_UNLOCK = eSaAmfAdminOperationIdT.SA_AMF_ADMIN_UNLOCK
ADMIN_LOCK = eSaAmfAdminOperationIdT.SA_AMF_ADMIN_LOCK
ADMIN_LOCK_IN = eSaAmfAdminOperationIdT.SA_AMF_ADMIN_LOCK_INSTANTIATION
ADMIN_UNLOCK_IN = eSaAmfAdminOperationIdT.SA_AMF_ADMIN_UNLOCK_INSTANTIATION
accessor = None


def find_object_type(class_name, parent_list):
    """ Find objects of a certain class under a parent list
        return: list of ImmObjects
    """
    result = []
    for par in parent_list:
        _iter = inst_iter(class_name, par.dn)
        _iter.init()
        for immobj in _iter:
            result.append(immobj)
    return result


def find_node_dns(hostname):
    """ Find the DNs of CLM and AMF node for the hostname
        returns: AMF node DN and CLM node DN
    """
    _iter = inst_iter('SaAmfNode')
    _iter.init()
    for node in _iter:
        # Get the first value part of the DN
        hname = node.saAmfNodeClmNode.split(',')[0].split('=')[1]
        if hname == hostname:
            return node.dn, node.saAmfNodeClmNode
    raise Exception('Could not find IMM object for hostname [%s]' % hostname)


def redundancy_of_su(su_dn):
    """ The redundancy of a SU
        returns: saAmfSgtRedundancyModel attribute value
    """
    # Get the SG DN from the SU DN
    sg_of_su = su_dn.split(',', 1)[1]
    _, itsg = accessor.get(sg_of_su)
    # Get the redundancy from the SG type
    _, itsg_t = accessor.get(itsg.saAmfSGType)
    return itsg_t.saAmfSgtRedundancyModel


def find_sus(amfnode_dn, scalable_redundancy):
    """ Find all SUs hosted by a AMF node matching some redundancy models
        returns: list of SUs (ImmObject)
    """
    sus = []
    _iter = inst_iter('SaAmfSU')
    _iter.init()
    for itsu in _iter:
        if amfnode_dn == itsu.saAmfSUHostedByNode:
            if redundancy_of_su(itsu.dn) in scalable_redundancy:
                sus.append(itsu)
    return sus


def find_sis_apps(sus, redundancy):
    """ Match the SUs to SIs for a given redundancy model
        returns: The matched SIs as list of ImmObjects
                 The apps of SUs as list of DNs
    """
    matched_sus = []
    matched_sgs = []
    matched_apps = []
    protected_sis = []
    su_svctypes = []

    # Collect the SUs, SGs and Apps of a certain redundancy
    for itsu in sus:
        if redundancy_of_su(itsu.dn) == redundancy:
            matched_sus.append(itsu)
            # Get SG and App DNs from the SU DN
            matched_sgs.append(itsu.dn.split(',', 1)[1])
            matched_apps.append(itsu.dn.split(',', 2)[2])

    # Keep the order and make the items unique
    matched_apps = sorted(set(matched_apps), key=matched_apps.index)

    # Collect the SIs protected by the SGs
    _iter = inst_iter('SaAmfSI')
    _iter.init()
    for itsi in _iter:
        if itsi.saAmfSIProtectedbySG in matched_sgs:
            protected_sis.append(itsi)

    # Collect the SvcTypes of the SUs
    for itsu in matched_sus:
        _, su_type = accessor.get(itsu.saAmfSUType)
        for svc_type in su_type.saAmfSutProvidesSvcTypes:
            su_svctypes.append(svc_type)

    # Match SvcType in SU and SI
    result_sis = []
    for itsi in protected_sis:
        if itsi.saAmfSvcType in su_svctypes:
            result_sis.append(itsi)

    return result_sis, matched_apps


def find_node_groups(amf_node):
    """ fetch all node groups a node belongs to """
    matching_groups = []
    _iter = inst_iter('SaAmfNodeGroup')
    _iter.init()
    for ngrp in _iter:
        if str.find(''.join(ngrp.saAmfNGNodeList), amf_node) >= 0:
            matching_groups.append(ngrp)
    return matching_groups


def scale_in(hostname):
    """ Remove the configuration for the host node """
    print('-Scaling in: %s' % hostname)
    amfnode_dn, clmnode_dn = find_node_dns(hostname)
    _, clmnode = accessor.get(clmnode_dn)
    _, amfnode = accessor.get(amfnode_dn)

    print("lock/lock-in %s %s" % (clmnode_dn, amfnode_dn))
    subprocess.call(['amf-adm', 'lock', clmnode_dn])
    subprocess.call(['amf-adm', 'lock', amfnode_dn])
    subprocess.call(['amf-adm', 'lock-in', amfnode_dn])

    sus = find_sus(amfnode_dn, [TWO_N, NWAYACTIVE, NORED])

    ccb = Ccb(flags=None)
    ccb.init()

    for itsu in sus:
        print(itsu.dn)
        subprocess.call(['amf-adm', 'lock', itsu.dn])
        subprocess.call(['amf-adm', 'lock-in', itsu.dn])
        ccb.delete(itsu.dn)

    print('-Stop opensafd on %s' % hostname)
    subprocess.call(["immadm", "-o", "5", "-p", "saClmAction:SA_STRING_T:stop", clmnode_dn])

    sis, apps = find_sis_apps(sus, NORED)
    for itsi in sis:
        # Check if this SI has a assignment
        siass = inst_iter('SaAmfSIAssignment')
        siass.init()
        assigned = [ass for ass in siass if str.find(ass.dn, itsi.dn) != -1]

        # Check if the SU App is used by this SI... Why? Not sure, the example
        # I followed did even more stuff here. TODO: Investigate why.
        usedapp = [app for app in apps if str.find(itsi.dn, app) != -1]
        si_app = itsi.dn.split(',')[1:][0]  # Last split is the SI App
        if not assigned and usedapp and si_app in apps:
            csis = find_object_type('SaAmfCSI', [itsi])
            for csi in csis:
                print(csi.dn)
                ccb.delete(csi.dn)
            print(itsi.dn)
            ccb.delete(itsi.dn)

    print("-Update node groups")
    node_groups = find_node_groups(amfnode_dn)
    for ngr in node_groups:
        ccb.modify_value_delete(ngr.dn, "saAmfNGNodeList", amfnode_dn)

    ccb.delete(amfnode.dn)
    ccb.delete(clmnode.dn)

    ccb.apply()
    print('-Scaling in done')


if __name__ == '__main__':
    accessor = ImmOmAccessor()
    accessor.init()

    parser = argparse.ArgumentParser(
        description='Scales OpenSAF by adding and removing node configuration')
    parser.add_argument(
        '--hostname', type=str, required=True,
        help='Hostname for the new node.')

    args = parser.parse_args()

    scale_in(args.hostname)
