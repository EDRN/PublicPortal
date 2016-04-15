# encoding: utf-8
# Copyright 2015 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.
#
# set-rdf-sources - configure RDF URLs

app = globals().get('app', None)  # ``app`` comes from ``instance run`` magic.
portalID = 'edrn'

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy, OmnipotentUser
from Testing import makerequest
from zope.app.component.hooks import setSite
import optparse, logging, sys, transaction

# Defaults
DEF_BODY_SYSTEMS = 'https://edrn-dev.jpl.nasa.gov/dmcc/rdf-data/body-systems/@@rdf'
DEF_DISEASES     = 'https://edrn-dev.jpl.nasa.gov/dmcc/rdf-data/diseases/@@rdf'
DEF_RESOURCES    = 'https://edrn.jpl.nasa.gov/bmdb/rdf/resources'
DEF_PUBLICATIONS = 'https://edrn-dev.jpl.nasa.gov/dmcc/rdf-data/publications/@@rdf'
DEF_ADD_PUBS     = 'http://edrn.jpl.nasa.gov/bmdb/rdf/publications'
DEF_SITES        = 'https://edrn-dev.jpl.nasa.gov/dmcc/rdf-data/sites/@@rdf'
DEF_PEOPLE       = 'https://edrn-dev.jpl.nasa.gov/dmcc/rdf-data/registered-person/@@rdf'
DEF_COMMITTEES   = 'https://edrn-dev.jpl.nasa.gov/dmcc/rdf-data/committees/@@rdf'
DEF_BIOMARKERS   = 'https://edrn.jpl.nasa.gov/bmdb/rdf/biomarkers?qastate=all'
DEF_BMO          = 'https://edrn.jpl.nasa.gov/bmdb/rdf/biomarkerorgans?qastate=all'
DEF_BIOMUTA      = 'https://edrn-dev.jpl.nasa.gov/dmcc/rdf-data/biomuta/@@rdf'
DEF_PROTOCOLS    = 'https://edrn-dev.jpl.nasa.gov/dmcc/rdf-data/protocols/@@rdf'

# Set up logging
_logger = logging.getLogger('set-rdf-sources')
_logger.setLevel(logging.INFO)
_console = logging.StreamHandler(sys.stderr)
_formatter = logging.Formatter('%(levelname)-8s %(message)s')
_console.setFormatter(_formatter)
_logger.addHandler(_console)

# Set up command-line options
_optParser = optparse.OptionParser(usage='Usage: %prog [options]')
_optParser.add_option(
    '--body-systems', default=DEF_BODY_SYSTEMS, metavar='URL',
    help='Set body systems RDF source to URL, default "%ddefautl"'
)
_optParser.add_option(
    '--diseases', default=DEF_DISEASES, metavar='URL',
    help='Set diseases RDF source to URL, default "%default"'
)
_optParser.add_option(
    '--resources', default=DEF_RESOURCES, metavar='URL',
    help='Set misc resources RDF source to URL, default "%default"'
)
_optParser.add_option(
    '--publications', default=DEF_PROTOCOLS, metavar='URL',
    help='Set publications RDF source to URL, default "%default"'
)
_optParser.add_option(
    '--additional-publications', default=DEF_ADD_PUBS, metavar='URL',
    help='Set the additional publications RDF source to URL, default "%default"'
)
_optParser.add_option(
    '--sites', default=DEF_SITES, metavar='URL',
    help='Set sites RDF source to URL, default "%default"'
)
_optParser.add_option(
    '--people', default=DEF_PEOPLE, metavar='URL',
    help='Set people RDF source to URL, default "%default"'
)
_optParser.add_option(
    '--committees', default=DEF_COMMITTEES, metavar='URL',
    help='Set committees RDF source to URL, default "%default"'
)
_optParser.add_option(
    '--biomarkers', default=DEF_BIOMARKERS, metavar='URL',
    help='Set biomarkers RDF source to URL, default "%default"'
)
_optParser.add_option(
    '--biomarker-organs', default=DEF_BMO, metavar='URL',
    help='Set biomaker-organs RDF source to URL, default "%default'
)
_optParser.add_option(
    '--biomuta', default=DEF_BIOMUTA, metavar='URL',
    help='Set biomuta RDF source to URL, default "%default"'
)
_optParser.add_option(
    '--protocols', default=DEF_PROTOCOLS, metavar='URL',
    help='Set protocols RDF soruce to URL, default "%default"'
)
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


def setRDFSources(
    app, portalID, organs, diseases, resources, publications, addPubs, sites, people, committees,
    bm, bmo, biomuta, protocols
):
    _logger.info('Setting RDF sources on portal "%s"', portalID)
    app = makerequest.makerequest(app)
    setupZopeSecurity(app)
    portal = getPortal(app, portalID)
    if 'resources' in portal.keys() and 'body-systems' in portal['resources'].keys():
        _logger.info('Setting body-systems to %s', organs)
        bodySystems = portal['resources']['body-systems']
        bodySystems.rdfDataSource = organs
    else:
        _logger.debug('No resources/body-systems folder found')
    if 'resources' in portal.keys() and 'diseases' in portal['resources'].keys():
        _logger.info('Setting diseases to %s', diseases)
        d = portal['resources']['diseases']
        d.rdfDataSource = diseases
    else:
        _logger.debug('No resources/diseases folder found')
    if 'resources' in portal.keys() and 'miscellaneous-resources' in portal['resources'].keys():
        _logger.info('Setting miscellaneous-resources to %s', resources)
        misc = portal['resources']['miscellaneous-resources']
        misc.rdfDataSource = resources
    else:
        _logger.debug('No resources/miscellaneous-resources folder found')
    if 'publications' in portal.keys():
        _logger.info('Setting publications to %s', publications)
        pubs = portal['publications']
        pubs.rdfDataSource, pubs.additionalDataSources = publications, [addPubs]
    else:
        _logger.debug('No publications folder found')
    if 'sites' in portal.keys():
        _logger.info('Setting sites and people to %s and %s respectively', sites, people)
        s = portal['sites']
        s.rdfDataSource, s.peopleDataSource = sites, people
    else:
        _logger.debug('No sites folder found')
    if 'committees' in portal.keys():
        _logger.info('Setting committees to %s', committees)
        c = portal['committees']
        c.rdfDataSource = committees
    else:
        _logger.debug('No committees folder found')
    if 'biomarkers' in portal.keys():
        _logger.info('Setting sources for biomarkers to %s, %s, and %s', bm, bmo, biomuta)
        biomarkers = portal['biomarkers']
        biomarkers.rdfDataSource, biomarkers.bmoDataSource, biomarkers.bmuDataSource = bm, bmo, biomuta
    else:
        _logger.debug('No biomarkers folder found')
    if 'protocols' in portal.keys():
        _logger.info('Setting protocols to %s', protocols)
        p = portal['protocols']
        p.rdfDataSource = protocols
    else:
        _logger.debug('No protocols folder found')
    transaction.commit()


def main(argv):
    options, args = _optParser.parse_args(argv)
    if len(args) > 1:
        _optParser.error('This script takes no arguments (only options)')
    if options.verbose:
        _logger.setLevel(logging.DEBUG)
    global app, portalID
    setRDFSources(
        app,
        portalID,
        options.body_systems,
        options.diseases,
        options.resources,
        options.publications,
        options.additional_publications,
        options.sites,
        options.people,
        options.committees,
        options.biomarkers,
        options.biomarker_organs,
        options.biomuta,
        options.protocols
    )
    return True

if __name__ == '__main__':
    # The [2:] works around plone.recipe.zope2instance-4.2.6's lame bin/interpreter script issue
    sys.exit(0 if main(sys.argv[2:]) is True else -1)

