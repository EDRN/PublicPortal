# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.
#
# setupldap - set up LDAP in the EDRN Portal

app = globals().get('app', None) # ``app`` comes from ``instance run`` magic.
portalID = 'edrn'

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from Testing import makerequest
from zope.component.hooks import setSite
from Products.CMFCore.utils import getToolByName
import optparse, logging, sys, getpass, transaction, urlparse
from plone.app.ldap.engine.interfaces import ILDAPConfiguration
from plone.app.ldap.engine.schema import LDAPProperty
from zope.component import getUtility
from plone.app.ldap.ploneldap.util import guaranteePluginExists
from Products.PluggableAuthService.interfaces.plugins import (
    IAuthenticationPlugin, IPropertiesPlugin, IUserAdderPlugin
)
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy, OmnipotentUser
from AccessControl.SecurityManager import setSecurityPolicy

# Set up logging
_logger = logging.getLogger('setupldap')
_logger.setLevel(logging.DEBUG)
_console = logging.StreamHandler(sys.stderr)
_formatter = logging.Formatter('%(levelname)-8s %(message)s')
_console.setFormatter(_formatter)
_logger.addHandler(_console)

# Set up command-line options
_optParser = optparse.OptionParser(usage='Usage: %prog [options]')
_optParser.add_option('-D', '--system-dn', default='uid=admin,ou=system', metavar='DN',
    help='Set LDAP admin username to DN, default "%default"')
_optParser.add_option('-w', '--password', help='Set LDAP admin password to PASSWORD')
_optParser.add_option('-W', '--prompt', action='store_true', help='Prompt for LDAP admin password; suppresses "-w"')
_optParser.add_option('-H', '--ldap-url', default='ldap://localhost', help='URL to LDAP server, default "%default"')
_optParser.add_option('-v', '--verbose', action='store_true', help='Be overly verbose')

def setupZopeSecurity(app):
    _logger.debug('Setting up Zope security')
    acl_users = app.acl_users
    setSecurityPolicy(PermissiveSecurityPolicy())
    newSecurityManager(None, OmnipotentUser().__of__(acl_users))

def getPortal(app, portalID):
    _logger.debug('Getting portal "%s"', portalID)
    portal = getattr(app, portalID)
    setSite(portal)
    return portal

def deleteLDAPPlugins(portal):
    _logger.info('Deleting all LDAP user folders in "%r"', portal)
    acl_users = getattr(portal, 'acl_users')
    ids = [o.id for o in [acl_users[i] for i in acl_users.objectIds()] if o.meta_type == 'Plone LDAP plugin']
    _logger.debug('Deleting %d LDAP folder%s', len(ids), 's' if len(ids) != 1 else '')
    acl_users.manage_delObjects(ids)

def reloadLDAPSetup(portal):
    _logger.info('Reloading add-on LDAP Setup')
    qi = getToolByName(portal, 'portal_quickinstaller')
    if 'plone.app.ldap' in [i['id'] for i in qi.listInstalledProducts()]:
        _logger.debug('Found plone.app.ldap, uninstalling it')
        qi.uninstallProducts(['plone.app.ldap'])
    _logger.debug('Installing plone.app.ldap')
    qi.installProduct('plone.app.ldap')

def parseURL(ldapURL):
    p = urlparse.urlparse(ldapURL)
    colon = p.netloc.find(':')
    if colon == -1:
        host, port = p.netloc, '389' if p.scheme == 'ldap' else '636'
    else:
        host, port = p.netloc[:colon], p.netloc[colon+1:]
    return p.scheme, host, port

def createLDAPPlugin(portal, ldapURL, systemDN, passwd):
    _logger.info('Creating new LDAP plugin for "%s"', ldapURL)
    scheme, hostname, port = parseURL(ldapURL)
    ldapConfig = getUtility(ILDAPConfiguration)
    _logger.debug('Setting up labels for existing schemata')
    p = ldapConfig.schema['uid']
    p.ldap_name, p.plone_name, p.description, p.multi_valued = 'uid', '', u'User ID', False
    p = ldapConfig.schema['mail']
    p.ldap_name, p.plone_name, p.description, p.multi_valued = 'mail', 'email', u'Email Address', False
    p = ldapConfig.schema['cn']
    p.ldap_name, p.plone_name, p.description, p.multi_valued = 'cn', 'fullname', u'Full Name', False
    p = ldapConfig.schema['sn']
    p.ldap_name, p.plone_name, p.description, p.multi_valued = 'sn', '', u'Surname', False
    _logger.debug('Adding mapping for "description" schema')
    ldapConfig.schema['description'] = LDAPProperty('description', 'description', u'Description', False)
    _logger.debug('Setting up basic LDAP attributes')
    ldapConfig.userid_attribute    = 'uid'
    ldapConfig.user_object_classes = 'edrnPerson'
    ldapConfig.ldap_type           = u'LDAP'
    ldapConfig.user_scope          = 1 # one level
    ldapConfig.user_base           = 'dc=edrn,dc=jpl,dc=nasa,dc=gov'
    ldapConfig.rdn_attribute       = 'uid'
    ldapConfig.login_attribute     = 'uid'
    ldapConfig.group_scope         = 1 # one level
    ldapConfig.group_base          = 'dc=edrn,dc=jpl,dc=nasa,dc=gov'
    ldapConfig.bind_password       = passwd
    ldapConfig.bind_dn             = systemDN
    _logger.debug('Making sure LDAP plugin exists')
    guaranteePluginExists()
    _logger.debug('Setting negative cache to zero so Products.LoginLockout will work correctly')
    portal.acl_users['ldap-plugin'].acl_users.setCacheTimeout('negative', 0)
    # Add a server; we don't do it through plone.app.ldap because it assumes *all* LDAP servers are on ports 389 or 636.
    # We're more general than that.
    _logger.debug('Enabling connection to "%s"', ldapURL)
    inner = portal.acl_users['ldap-plugin'].acl_users
    inner.manage_addServer(hostname, port, use_ssl=1 if scheme == 'ldaps' else 0, conn_timeout=5, op_timeout=30)
    # Also, make Super Users have the Manager role
    _logger.debug('Adding Manager role to group "Super User"')
    inner.manage_addGroupMapping('Super User', 'Manager')

def setPluginOrder(plugins, interface, desiredOrder):
    _logger.debug('Setting plugin order for %r to %r', interface, desiredOrder)
    current = plugins[interface]
    toOrder = []
    for i in desiredOrder:
        if i in current:
            toOrder.append(i)
    plugins[interface] = tuple(toOrder)

def fixPASPlugins(portal):
    _logger.info('Re-ordering plugins in the Pluggable Auth Service')
    acl_users = getattr(portal, 'acl_users')
    plugins = acl_users.plugins._plugins
    setPluginOrder(plugins, IAuthenticationPlugin, ('source_users', 'session', 'ldap-plugin', 'login_lockout_plugin'))
    setPluginOrder(plugins, IPropertiesPlugin, ('ldap-plugin', 'mutable_properties'))
    setPluginOrder(plugins, IUserAdderPlugin, ('ldap-plugin', 'source_users'))

def setupLDAP(app, portalID, ldapURL, systemDN, systemDNpwd):
    _logger.info('Setting up LDAP on portal "%s"', portalID)
    _logger.info('Using LDAP at "%s" with system DN "%s" and password [REDACTED]', ldapURL, systemDN)
    app = makerequest.makerequest(app)
    setupZopeSecurity(app)
    portal = getPortal(app, portalID)
    deleteLDAPPlugins(portal)
    reloadLDAPSetup(portal)
    createLDAPPlugin(portal, ldapURL, systemDN, systemDNpwd)
    fixPASPlugins(portal)
    _logger.debug('Committing transactions')
    transaction.commit()
    _logger.debug('Withdrawing security manager')
    noSecurityManager()
    _logger.debug('All done')

def main(argv):
    options, args = _optParser.parse_args(argv)
    if len(args) > 1: 
        _optParser.error('This script takes no arguments (only options)')
    systemDN, ldapURL = options.system_dn, options.ldap_url
    if options.prompt:
        systemDNpwd = getpass.getpass(u'Password for "%s": ' % systemDN)
    else:
        if options.password:
            systemDNpwd = options.password
        else:
            _optParser.error('Please specify a password with -w or ask for a password prompt with -W')
    if options.verbose:
        _logger.setLevel(logging.DEBUG)
    global app, portalID
    setupLDAP(app, portalID, ldapURL, systemDN, systemDNpwd)
    return True

if __name__ == '__main__':
    # The [2:] works around plone.recipe.zope2instance-4.2.6's lame bin/interpreter script issue
    sys.exit(0 if main(sys.argv[2:]) is True else -1)

