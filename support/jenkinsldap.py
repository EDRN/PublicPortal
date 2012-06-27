# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.
#
# Reset LDAP when the portal's built by Jenkins on tumor.jpl.nasa.gov to point to Apache DS on the localhost.
#
# Execute with a Zope instance's "run" command, ie:
#   bin/instance-debug run support/jenkinsldap.py [ADMINUSER] [LDAPPASSWORD]
# where ADMINUSER is the optional name of the Zope manager user account, and LDAPPASSWORD is the password
# for the LDAP manager user account.
# 
# Assumes that the instance already has a previous edition of the EDRN portal installed.

_adminUser = 'admin' # Name of the Zope administrative user
_ldapPassword = 'secret' # Password for uid=admin,ou=system
_ldapConfig = '/usr/local/edrn-directory/current/ops.cfg'

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from Testing import makerequest
from zope.app.component.hooks import setSite
import transaction, sys, ConfigParser

def getLDAPPassword():
    try:
        cp = ConfigParser.SafeConfigParser()
        cp.read([_ldapConfig])
        pw = cp.get('passwords', 'system-dn')
        print >>sys.stderr, 'Got system-dn password from %s' % _ldapConfig
        return pw
    except:
        print >>sys.stderr, "Can't read system-dn password from %s; using default password" % _ldapConfig
        return _ldapPassword

def main(app, adminUser):
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

    # Get the portal and its acl users
    portal = getattr(app, 'edrn')
    setSite(portal)
    acl_users = getattr(portal, 'acl_users')

    # Nuke the old OpenLDAP-connected plugin, if any
    if 'ldapdmcc' in acl_users.objectIds():
        print >>sys.stderr, 'Getting rid of ldapdmcc'
        acl_users.manage_delObjects('ldapdmcc')

    # Set the password
    print >>sys.stderr, 'Setting LDAP system-dn password'
    acl_users = getattr(acl_users, 'ldap')
    ldapUserFolder = getattr(acl_users, 'acl_users')
    ldapUserFolder._bindpwd = getLDAPPassword()

    # Get rid of all LDAP servers
    print >>sys.stderr, 'Nuking all existing LDAP servers'
    servers = ldapUserFolder.getServers()
    ldapUserFolder.manage_deleteServers(range(len(servers)))

    # Now set up just the testing ApacheDS
    print >>sys.stderr, 'Adding local ApacheDS'
    ldapUserFolder.manage_addServer('localhost', '389', use_ssl=0, conn_timeout=5, op_timeout=30)

    # Commit everything and shut down.
    transaction.commit()
    noSecurityManager()
    return True

if __name__ == '__main__':
    adminUser = sys.argv[1] if len(sys.argv) == 2 else _adminUser
    rc = main(app, adminUser) # ``app`` comes from ``instance run`` magic.
    sys.exit(rc and 0 or -1)
