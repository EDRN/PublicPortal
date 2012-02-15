# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.
#
# Adapted from Finn Arild Aasheim's script:
# http://svn.finnarild.com/svn/scripts/fixinterfaces.py
# 
# See more at http://plone.org/documentation/kb/cleaning-p4a

from transaction import commit
from p4a.video.interfaces import IVideoSupport
from p4a.audio.interfaces import IAudioSupport
from p4a.calendar.interfaces import ICalendarSupport
from p4a.plonevideoembed.interfaces import IVideoLinkSupport
from p4a.calendar.interfaces import ICalendarEnhanced
from p4a.subtyper.interfaces import ISubtyped
from zope.interface import noLongerProvides
from zope.component import getSiteManager
from Products.CMFCore.utils import getToolByName
import sys

class fixp4a:
    def __init__(self, site):
        self.site = site
        self.rmIV()
    
    def rmIV(self):
        finn = self.site
        self.removeUtility(finn, IVideoSupport)
        self.removeUtility(finn, ICalendarSupport)
        self.removeUtility(finn, IVideoLinkSupport)
        self.removeUtility(finn, IAudioSupport)
        self.removeUtility(finn, ISubtyped)
        self.removeUtility(finn, ICalendarEnhanced)
        self.removep4a(finn)
        self.removeinterfaces(finn)
        commit()

    def removeinterfaces(self, site):
        pc = site.portal_catalog
        res = pc.searchResults()
        for n in res:
            try:
                obj = n.getObject()
                noLongerProvides(obj, ISubtyped)
                noLongerProvides(obj, ICalendarEnhanced)
            except:
                continue

    def removep4a(self, site):
        sm = site.getSiteManager()
        provided = sm.utilities._provided
        for x in provided.keys():
            if x.__module__.find('p4a') != -1:
                print "removing %s" % x
                del provided[x]
        sm.utilities._provided = provided

    def removeUtility(self, site, Interface):
        try:
            sm = site.getSiteManager()
            util = sm.getUtility(Interface)
            sm.unregisterUtility(provided=Interface)
            del util
            sm.utilities.unsubscribe((), Interface)
            del sm.utilities.__dict__['_provided'][Interface]
            del sm.utilities._subscribers[0][Interface]
        except:
            pass

def main(app):
    portal = app['edrn']
    # Get rid of some packages
    qi = getToolByName(portal, 'portal_quickinstaller')
    qi.uninstallProducts(['eea.facetednavigation', 'eea.jquery', 'p4a.subtyper'])
    # Run finnarild's part (btw, why is it a class instead of a function?)
    fixp4a(portal)
    # Now clean out the adapter that finnarild's part missed
    sm = getSiteManager(portal)
    registrations = tuple(sm.registeredAdapters())
    for registration in registrations:
        if registration.name == u'subtypes':
            factory, required, provided = registration.factory, registration.required, registration.provided
            sm.unregisterAdapter(factory=factory, required=required, provided=provided, name=registration.name)
            break
    # Done
    commit()
    app._p_jar.sync()
    return True


if __name__ == '__main__':
    rc = main(app) # ``app`` comes from ``instance run`` magic.
    sys.exit(rc and 0 or -1)

