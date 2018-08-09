# encoding: utf-8
# Copyright 2010–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.
#
# Upgrade an existing installation of the EDRN public portal.
#
# Execute with a Zope instance's "run" command, ie:
#   bin/instance-debug run support/upgrade.py
# 
# Assumes that the instance already has a previous edition of the EDRN portal installed.

_adminUser = 'admin'            # Name of the Zope administrative user
_adminPass = 'admin'            # Default password
_policy    = 'edrnsite.policy'  # Name of the policy that orchestrates everything
_siteID    = 'edrn'             # Object ID of the PloneSite object in the Zope app server

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from Products.CMFCore.utils import getToolByName
from Testing import makerequest
from zope.component.hooks import setSite
import transaction, sys, logging
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy, OmnipotentUser
from AccessControl.SecurityManager import setSecurityPolicy

def main(app, siteID, adminUser, adminPass, policy):
    # Get logging
    channel = logging.StreamHandler()
    channel.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
    for logname in ('edrnsite', 'eke'):
        logger = logging.getLogger(logname)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(channel)

    # Get a test request installed.
    app = makerequest.makerequest(app)

    # Nuke all old admin users
    acl_users = app.acl_users
    admins = [i for i in acl_users.users.listUserIds()]
    for i in admins:
        acl_users.users.removeUser(i)

    # Add our new admin user
    acl_users.users.manage_addUser(adminUser, adminUser, adminPass, adminPass)

    # Set up security.
    setSecurityPolicy(PermissiveSecurityPolicy())
    newSecurityManager(None, OmnipotentUser().__of__(acl_users))

    # Get the portal.
    portal = app.unrestrictedTraverse(siteID)
    portal.setupCurrentSkin(app.REQUEST)
    setSite(portal)

    # Disable CacheFu.  If we don't, the CMF Squid Tool will start a purge thread, and that
    # purge thread isn't a daemon thread (it probably should be).  Since it's not a daemon,
    # we won't ever terminate.  Note also that CacheFu died out with Plone 3, but this code
    # is pretty harmless so I'm leaving it for historical reasons.
    cacheTool = getToolByName(portal, 'portal_cache_settings', None)
    if cacheTool:
        if hasattr(cacheTool, 'setEnabled'): cacheTool.setEnabled(False)
        if hasattr(cacheTool, 'setDomains'): cacheTool.setDomains([])

    # Upgrade Plone
    migrationTool = getToolByName(portal, 'portal_migration')
    migrationTool.upgrade(dry_run=False)

    # Upgrade the EDRN site
    qi = getToolByName(portal, 'portal_quickinstaller')
    qi.upgradeProduct('edrnsite.policy')

    # Commit everything and shut down.
    transaction.commit()
    noSecurityManager()
    return True

if __name__ == '__main__':
    adminUser = sys.argv[1] if len(sys.argv) >= 2 else _adminUser
    adminPass = sys.argv[2] if len(sys.argv) >= 3 else _adminPass
    rc = main(app, _siteID, adminUser, adminPass, _policy) # ``app`` comes from ``instance run`` magic.
    sys.exit(rc and 0 or -1)
