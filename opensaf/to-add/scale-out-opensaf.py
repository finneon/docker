#!/usr/bin/env python
""" Add IMM configuration for new nodes join the cluster
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


def print_object(immobj, new_dn=None):
    """ Print an ImmObject and attributes with the type enum """
    if new_dn:
        print(new_dn)
    else:
        print(immobj.dn)
    for key, value in immobj.attrs.iteritems():
        val = ''
        if value[1]:
            val = value[1]
            if value[1][0]:
                val = value[1][0]
        if val:
            print('\t{0}: {1} : {2}'.format(key, val, value[0]))


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


def prepare_for_write(objects):
    """ Prepare objects for write by removing runtime attributes
        returns: List of ImmObjects without runtime attributes
    """
    conf_objects = []
    for immobj in objects:
        _, immobj = accessor.get(immobj.dn, ['SA_IMM_SEARCH_GET_CONFIG_ATTR'])
        del immobj.attrs['SaImmAttrAdminOwnerName']
        del immobj.attrs['SaImmAttrClassName']
        del immobj.attrs['SaImmAttrImplementerName']
        conf_objects.append(immobj)
    return conf_objects


def find_node_groups(amf_node):
    """ Fetch all node groups a node belongs to """
    matching_groups = []
    _iter = inst_iter('SaAmfNodeGroup')
    _iter.init()
    for ngrp in _iter:
        if str.find(''.join(ngrp.saAmfNGNodeList), amf_node) >= 0:
            matching_groups.append(ngrp)
    return matching_groups


def collect_scalable_immobjects(from_amfnode_dn, from_clmnode_dn):
    """ Read AMF objects of an allowed type and redundancy from a node.
        returns: list of collected ImmObjects
    """
    sus = find_sus(from_amfnode_dn, [TWO_N, NWAYACTIVE, NORED])
    comps = find_object_type('SaAmfComp', sus)
    hchks = find_object_type('SaAmfHealthcheck', comps)
    comps_cs = find_object_type('SaAmfCompCsType', comps)
    sis, _ = find_sis_apps(sus, NORED)
    csis = find_object_type('SaAmfCSI', sis)
    csiattrs = find_object_type('SaAmfCSIAttribute', csis)

    swbundles = []
    _iter = inst_iter(class_name='SaAmfNodeSwBundle', root_name=from_amfnode_dn)
    _iter.init()
    for immobj in _iter:
        swbundles.append(immobj)

    _, from_amfnode = accessor.get(from_amfnode_dn)
    _, from_clmnode = accessor.get(from_clmnode_dn)

    # Order is important
    return [from_amfnode, from_clmnode] + sus + sis + csis + comps + \
        comps_cs + swbundles + hchks + csiattrs


def modify_immobject(immobj, suffix, new_amfnode_dn, new_hostname):
    """ Rename DN and change attributes for one IMM object """
    rename_str = None
    immobj.new_dn = immobj.dn
    match = re.search('safSu=[^,]*|safSi[^,]*', immobj.new_dn)
    if match:
        # We have a SU or SI in the DN string. Generate a hash from it.
        rename_str = immobj.new_dn[match.start():match.end()] + new_hostname
        rename_str += suffix
        rename_str = hashlib.md5(rename_str).hexdigest()[:10]

    # Rename the DN and store it in new_dn
    immobj.new_dn = re.sub(r'(safSu|safSi)=([^,]*),', r'\1={0},'.
                           format(rename_str), immobj.new_dn)
    immobj.new_dn = re.sub('safNode=[^,]*,', 'safNode={0},'.
                           format(new_hostname), immobj.new_dn)
    immobj.new_dn = re.sub('safAmfNode=[^,]*,', 'safAmfNode={0},'.
                           format(new_hostname), immobj.new_dn)

    # Change attributes to match the new node. Admin state is set to something
    # accepted by the AMF OI
    if immobj.class_name == 'SaAmfSU':
        immobj.saAmfSUHostNodeOrNodeGroup = new_amfnode_dn
        immobj.saAmfSUAdminState = ADMIN_UNLOCK

    elif immobj.class_name == 'SaAmfNode':
        immobj.saAmfNodeAdminState = ADMIN_LOCK_IN
        immobj.saAmfNodeClmNode = re.sub(
            'safNode=[^,]*,', 'safNode={0},'.format(new_hostname),
            immobj.saAmfNodeClmNode)


def split_rdn_and_parent(immobj):
    """ Split the DN of the passed in object into RDN and parent DN
        returns: RDN and parent DN as strings
    """
    rdn = immobj.new_dn.split(',', 1)[0]
    parent = immobj.new_dn.split(',', 1)[1]
    # Handle the case when we have two backslashes
    # At least here is object dn of SaAmfCompCsType class
    if re.search("\\\\", immobj.new_dn) and re.search("safC.*Type=", immobj.new_dn):
        parent = immobj.new_dn.split(',', 2)[-1]
        rdn = re.sub(",{0}".format(parent), "", immobj.new_dn)
    return rdn, parent


def scale_out(new_hostname, from_hostname):
    """ Scale out one node
        params:
            new_hostname - hostname of the new node
            from_hostname - hostname of the template node
    """
    print('-Scaling out to [%s] config copied from [%s]' % (new_hostname,
                                                            from_hostname))
    print(new_hostname)
    print(from_hostname)
    _iter = inst_iter('SaAmfSU')
    _iter.init()
    for itsu in _iter:
        # Get the first value part of the DN
        hname = itsu.saAmfSUHostedByNode.split(',')[0].split('=')[1]
        if hname == new_hostname:
            print('Node already has SUs, no scaling-out done')
            return 0

    from_amfnode_dn, from_clmnode_dn = find_node_dns(from_hostname)
    new_amfnode_dn = from_amfnode_dn.replace(from_hostname, new_hostname)
    objects = collect_scalable_immobjects(from_amfnode_dn, from_clmnode_dn)
    conf_objects = prepare_for_write(objects)

    suffix = str(time.time())
    for immobj in conf_objects:
        modify_immobject(immobj, suffix, new_amfnode_dn, new_hostname)

    objs = list()
    allowed_objs = ['SaAmfNode', 'SaClmNode', 'SaAmfSU', 'SaAmfSI', 'SaAmfCSI', 'SaAmfComp',
                    'SaAmfCompCsType', 'SaAmfNodeSwBundle', 'SaAmfHealthcheck', 'SaAmfCSIAttribute']
    for obj in conf_objects:
        if obj.class_name in allowed_objs:
            objs.append(obj)

    ccb = Ccb(flags=None)
    ccb.init()

    for immobj in objs:
        rdn, parent = split_rdn_and_parent(immobj)
        immobj.attrs[immobj.rdn_attribute][1] = [rdn]
        print_object(immobj, immobj.new_dn)
        del immobj.attrs['new_dn']
        ccb.create(immobj, parent)

    nodegroups_to_join = find_node_groups(from_amfnode_dn)
    for ngr in nodegroups_to_join:
        ccb.modify_value_add(ngr.dn, "saAmfNGNodeList", new_amfnode_dn)
    ccb.apply()

    print("-Unlock-in/unlock %s" % new_amfnode_dn)
    subprocess.call(['amf-adm', 'unlock-in', new_amfnode_dn])
    subprocess.call(['amf-adm', 'unlock', new_amfnode_dn])

    print('-Scaling out done')


if __name__ == '__main__':
    accessor = ImmOmAccessor()
    accessor.init()

    parser = argparse.ArgumentParser(
        description='Scales OpenSAF by adding and removing node configuration')
    parser.add_argument(
        '--hostname', type=str, required=True,
        help='Hostname for the new node.')
    parser.add_argument(
        '--copy-from', type=str, required=False, help='Hostname of the '
        'existing node to use as template. If not set, the host where the '
        'command is executed will be used as template.',
        default=os.uname()[1])

    args = parser.parse_args()

    scale_out(args.hostname, args.copy_from)
