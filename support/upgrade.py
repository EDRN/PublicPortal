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
import transaction, sys

def main(app, siteID, adminUser, policy):
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
    # we won't ever terminate.
    cacheTool = getToolByName(portal, 'portal_cache_settings')
    if cacheTool:
        if hasattr(cacheTool, 'setEnabled'): cacheTool.setEnabled(False)
        if hasattr(cacheTool, 'setDomains'): cacheTool.setDomains([])

    # Upgrade the portal.
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
