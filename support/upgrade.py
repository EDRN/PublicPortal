# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.
#
# Upgrade an existing installation of the EDRN public portal.
#
# Execute with a Zope instance's "run" command, ie:
#   bin/instance-debug run support/upgrade.py
# 
# Assumes that the instance already has a previous edition of the EDRN portal installed.

_adminUser = 'admin'            # Name of the Zope administrative user
_policy    = 'edrnsite.policy'  # Name of the policy that orchestrates everything
_siteID    = 'edrn'             # Object ID of the PloneSite object in the Zope app server

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from Products.CMFCore.utils import getToolByName
from Testing import makerequest
from zope.app.component.hooks import setSite
import transaction, sys, logging

def main(app, siteID, adminUser, policy):
    # Get logging
    channel = logging.StreamHandler()
    channel.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
    for logname in ('edrnsite', 'eke'):
        logger = logging.getLogger(logname)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(channel)

    # Get a test request installed.
    app = makerequest.makerequest(app)

    # Set up security.
    acl_users = app.acl_users
    user = acl_users.getUser(adminUser)
    if user:
        user = user.__of__(acl_users)
        newSecurityManager(None, user)
    else:
        raise Exception('Admin user "%s" does not exist' % adminUser)

    # Get the portal.
    portal = getattr(app, siteID)
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
    adminUser = len(sys.argv) == 2 and sys.argv[1] or _adminUser
    rc = main(app, _siteID, adminUser, _policy) # ``app`` comes from ``instance run`` magic.
    sys.exit(rc and 0 or -1)
