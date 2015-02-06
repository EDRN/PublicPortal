# encoding: utf-8
# Copyright 2013 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

app = globals().get('app', None) # ``app`` comes from ``instance run`` magic.
portalID = 'edrn'

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from Testing import makerequest
from zope.app.component.hooks import setSite
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy, OmnipotentUser
from AccessControl.SecurityManager import setSecurityPolicy
import sys, cStringIO, csv, codecs

class UnicodeWriter(object):
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def setupZopeSecurity(app):
    acl_users = app.acl_users
    setSecurityPolicy(PermissiveSecurityPolicy())
    newSecurityManager(None, OmnipotentUser().__of__(acl_users))


def getPortal(app, portalID):
    portal = getattr(app, portalID)
    setSite(portal)
    return portal

class Investigator(object):
    def __init__(self, name, title):
        self.name, self.title = name, title
    def __unicode__(self):
        return self.name + u' | ' + self.title
    def __cmp__(self, other):
        return cmp(self.name + self.title, other.name + other.title)
    def __hash__(self):
        return hash(self.name) ^ hash(self.title)


class OrganInvestigator(Investigator):
    def __init__(self, organName, name, title):
        super(OrganInvestigator, self).__init__(name, title)
        self.organName = organName
    def __unicode__(self):
        return self.organName + u' | ' + super(OrganInvestigator, self).__unicode__()
    def __cmp__(self, other):
        return cmp(self.organName + self.name + self.title, other.organName + other.name + other.title)
    def __hash__(self):
        return hash(self.organName) ^ super(OrganInvestigator, self).__hash__()


def reportBiomarkersByPIByOrganInDanFormat(context):
    organPIs = {}
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog(object_provides='eke.biomarker.interfaces.IBiomarker')
    for i in results:
        biomarker = i.getObject()
        bmName, qaState = biomarker.title.strip(), biomarker.qaState
        for objectID in biomarker.keys():
            bbs = biomarker[objectID]
            if bbs.portal_type != 'Biomarker Body System': continue
            organName = bbs.getBodySystem().title
            for subObjectID in bbs.keys():
                bso = bbs[subObjectID]
                if bso.portal_type != 'Body System Study': continue
                protocol = bso.getProtocol()
                if protocol is None: continue
                piSite = coISite = None
                if protocol.getLeadInvestigatorSite() is not None:
                    pi = protocol.getLeadInvestigatorSite().getPrincipalInvestigator()
                    if pi is not None and len(pi.title.strip()) > 0:
                        piSite = protocol.getLeadInvestigatorSite()
                        investigator = OrganInvestigator(organName, pi.title.strip(), u'Lead Investigator')
                        biomarkers = organPIs.get(investigator, set())
                        biomarkers.add(bmName)
                        organPIs[investigator] = biomarkers
                if protocol.getCoordinatingInvestigatorSite() is not None:
                    if protocol.getCoordinatingInvestigatorSite() != piSite:
                        pi = protocol.getCoordinatingInvestigatorSite().getPrincipalInvestigator()
                        if pi is not None and len(pi.title.strip()) > 0:
                            coISite = protocol.getCoordinatingInvestigatorSite()
                            investigator = OrganInvestigator(organName, pi.title.strip(), u'Co-Investigator')
                            biomarkers = organPIs.get(investigator, set())
                            biomarkers.add(bmName)
                            organPIs[investigator] = biomarkers
                for site in protocol.getInvolvedInvestigatorSites():
                    if site == piSite or site == coISite: continue
                    pi = site.getPrincipalInvestigator()
                    if pi is not None and len(pi.title.strip()) > 0:
                        investigator = OrganInvestigator(organName, pi.title.strip(), u'Investigator')
                        biomarkers = organPIs.get(investigator, set())
                        biomarkers.add(bmName)
                        organPIs[investigator] = biomarkers
    organInvestigators = organPIs.keys()
    organInvestigators.sort()
    for organInvestigator in organInvestigators:
        biomarkers = organPIs[organInvestigator]
        print unicode(organInvestigator) + u' | ' + u', '.join(biomarkers)


def reportBiomarkersByPIInDanFormat(context):
    pis = {}
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog(object_provides='eke.biomarker.interfaces.IBiomarker')
    for i in results:
        biomarker = i.getObject()
        bmName, qaState, protocols = biomarker.title.strip(), biomarker.qaState, biomarker.getProtocols()
        if len(protocols) == 0: continue
        for protocol in protocols:
            piSite = coISite = None
            if protocol.getLeadInvestigatorSite() is not None:
                pi = protocol.getLeadInvestigatorSite().getPrincipalInvestigator()
                if pi is not None and len(pi.title.strip()) > 0:
                    piSite = protocol.getLeadInvestigatorSite()
                    investigator = Investigator(pi.title.strip(), u'Lead Investigator')
                    biomarkers = pis.get(investigator, set())
                    biomarkers.add(bmName)
                    pis[investigator] = biomarkers
            if protocol.getCoordinatingInvestigatorSite() is not None:
                if protocol.getCoordinatingInvestigatorSite() != piSite:
                    pi = protocol.getCoordinatingInvestigatorSite().getPrincipalInvestigator()
                    if pi is not None and len(pi.title.strip()) > 0:
                        coISite = protocol.getCoordinatingInvestigatorSite()
                        investigator = Investigator(pi.title.strip(), u'Co-Investigator')
                        biomarkers = pis.get(investigator, set())
                        biomarkers.add(bmName)
                        pis[investigator] = biomarkers
            for site in protocol.getInvolvedInvestigatorSites():
                if site == piSite or site == coISite: continue
                pi = site.getPrincipalInvestigator()
                if pi is not None and len(pi.title.strip()) > 0:
                    investigator = Investigator(pi.title.strip(), u'Investigator')
                    biomarkers = pis.get(investigator, set())
                    biomarkers.add(bmName)
                    pis[investigator] = biomarkers
    investigators = pis.keys()
    investigators.sort()
    for investigator in investigators:
        biomarkers = pis[investigator]
        print unicode(investigator) + u' | ' + u', '.join(biomarkers)


def reportPIsbyBiomarkerInDanFormat(context):
    biomarkers, allInvestigators = {}, set()
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog(object_provides='eke.biomarker.interfaces.IBiomarker')
    for i in results:
        biomarker = i.getObject()
        name, qaState, protocols = biomarker.title.strip(), biomarker.qaState, biomarker.getProtocols()
        if len(protocols) == 0: continue
        investigators = set()
        for protocol in protocols:
            if protocol.piName is not None and len(protocol.piName.strip()) > 0:
                investigators.add(protocol.piName.strip())
            for site in protocol.getInvolvedInvestigatorSites():
                pi = site.getPrincipalInvestigator()
                if pi is not None and len(pi.title.strip()) > 0:
                    investigators.add(pi.title.strip())
        allInvestigators |= investigators
        pis = biomarkers.get(name, set())
        pis |= investigators
        biomarkers[name] = pis
    bmNames = biomarkers.keys()
    bmNames.sort()
    for bmName in bmNames:
        pis = biomarkers[bmName]
        print bmName + u' | ' + u', '.join(pis)


def generatePIsbyBiomakerInCSV(context):
    biomarkers, allInvestigators = {}, set()
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog(object_provides='eke.biomarker.interfaces.IBiomarker')
    for i in results:
        biomarker = i.getObject()
        name, qaState, protocols = biomarker.title.strip(), biomarker.qaState, biomarker.getProtocols()
        if len(protocols) == 0: continue
        investigators = set()
        for protocol in protocols:
            if protocol.piName is not None and len(protocol.piName.strip()) > 0:
                investigators.add(protocol.piName.strip())
            for site in protocol.getInvolvedInvestigatorSites():
                pi = site.getPrincipalInvestigator()
                if pi is not None and len(pi.title.strip()) > 0:
                    investigators.add(pi.title.strip())
        allInvestigators |= investigators
        pis = biomarkers.get(name, set())
        pis |= investigators
        biomarkers[name] = pis
    allInvestigators = list(allInvestigators)
    allInvestigators.sort()
    header = [u'Biomarker']
    header.extend(allInvestigators)
    with open('biomarkers.csv', 'wb') as f:
        writer = UnicodeWriter(f)
        writer.writerow(header)
        bmNames = biomarkers.keys()
        bmNames.sort()
        for bmName in bmNames:
            pis = biomarkers[bmName]
            row = [bmName]
            for piName in allInvestigators:
                if piName in pis:
                    row.extend(u'✗')
                else:
                    row.extend(u' ')
            writer.writerow(row)


def printAllBiomarkers(context):
    catalog, uidCatalog = getToolByName(context, 'portal_catalog'), getToolByName(context, 'uid_catalog')
    results = catalog(object_provides='eke.biomarker.interfaces.IBiomarker')
    biomarkers = {}
    for i in results:
        biomarker = i.getObject()    
        name, protocols = biomarker.title, biomarker.getProtocols()
        if len(protocols) == 0:
            biomarkers[name] = []
        else:
            biomarkers[name] = [u'{} ({})'.format(j.title, j.identifier) for j in protocols]
    names = biomarkers.keys()
    names.sort()
    with open('report.csv', 'wb') as f:
        writer = UnicodeWriter(f)
        for name in names:
            row = [name]
            row.extend(biomarkers[name])
            writer.writerow(row)

def printTabularBiomarkers(context):
    catalog = getToolByName(context, 'portal_catalog')
    class Organ(object):
        def __init__(self, name, numProtocols):
            self.name, self.numProtocols = name, numProtocols
        def __cmp__(self, other):
            return cmp(self.name, other.name)
        def __unicode__(self):
            #return u'{} ({} protocol{})'.format(self.name, self.numProtocols, u's' if self.numProtocols != 1 else u'')
            return self.name
        def __repr__(self):
            return 'Organ(%s,%d)' % (self.name, self.numProtocols)
    class Biomarker(object):
        def __init__(self, hgncName, name, protocols):
            self.hgncName, self.name, self.protocols = hgncName, name, protocols
            self.organs = []
            if not self.hgncName:
                self.hgncName = u'UNKNOWN HGNC'
            else:
                self.hgncName = unicode(self.hgncName)
        def __repr__(self):
            return 'Biomarker(%s,%s,%r)' % (self.hgncName, self.name, self.organs)
        def __cmp__(self, other):
            return cmp(self.hgncName, other.hgncName)
        def addOrgan(self, organName, numProtocols):
            self.organs.append(Organ(organName, numProtocols))
        def getRows(self):
            rows = []
            for organ in self.organs:
                organName = organ.name
                if len(self.protocols) == 0:
                    rows.append([self.hgncName, self.name, organName, u'UNKNOWN PROTOCOL'])
                else:
                    for protocol in self.protocols:
                        protocolName = protocol.title
                        pi = protocol.getLeadInvestigatorSite().getPrincipalInvestigator()
                        if pi is not None and len(pi.title.strip()) > 0:
                            piName = pi.title.strip()
                        else:
                            piName = u'UNKNONW PI'
                        rows.append([self.hgncName, self.name, organName, protocolName, piName])
            for row in rows:
                yield row
    results, biomarkers = catalog(object_provides='eke.biomarker.interfaces.IBiomarker'), []
    for i in results:
        biomarker = i.getObject()
        name, hgncName, protocols = biomarker.title, biomarker.hgncName, biomarker.getProtocols()
        b = Biomarker(hgncName, name, protocols)
        for objID, organObj in biomarker.contentItems():
            b.addOrgan(organObj.title, len(organObj.getProtocols()))
        biomarkers.append(b)
    biomarkers.sort()
    with open('report.csv', 'wb') as f:
        writer = UnicodeWriter(f)
        for biomarker in biomarkers:
            for row in biomarker.getRows():
                writer.writerow(row)

def printBiomarkersByPI(context):
    catalog, uidCatalog = getToolByName(context, 'portal_catalog'), getToolByName(context, 'uid_catalog')
    results = catalog(object_provides='eke.biomarker.interfaces.IBiomarker')
    pis, noProtocol, protocolNoPI = {}, [], []
    for i in results:
        biomarker = i.getObject()
        name, qaState, protocols = biomarker.title, biomarker.qaState, biomarker.getProtocols()
        # if qaState != 'Accepted': continue
        if len(protocols) == 0:
            noProtocol.append(name)
        else:
            for protocol in protocols:
                piName = protocol.piName
                if not piName:
                    protocolNoPI.append((name, protocol.title))
                else:
                    biomarkers = pis.get(piName, [])
                    if name not in biomarkers:
                        biomarkers.append(name)
                    pis[piName] = biomarkers
                
    sortPIs = pis.items()
    sortPIs.sort(lambda a, b: cmp(a[0], b[0]))
    for pair in sortPIs:
        biomarkers = pair[1]
        biomarkers.sort()
    noProtocol.sort()
    protocolNoPI.sort()
    print u'=== Principal Investigators ==='
    for pair in sortPIs:
        pi, biomarkers = pair
        print pi + u':'
        print u'\t' + u', '.join(biomarkers)
    print
    print u'=== Biomarkers with No Protocols (%d) ===' % len(noProtocol)
    for biomarker in noProtocol:
        print biomarker
    print
    print u'=== Biomarkers with a Protocol but no PI (%d) ===' % len(protocolNoPI)
    for pair in protocolNoPI:
        print pair



def main(argv):
    global app, portalID
    app = makerequest.makerequest(app)
    setupZopeSecurity(app)
    portal = getPortal(app, portalID)
    # Report 1:
    # reportPIsbyBiomarkerInDanFormat(portal)
    # Report 2:
    # reportBiomarkersByPIInDanFormat(portal)
    # Report 3:
    # reportBiomarkersByPIByOrganInDanFormat(portal)
    # Obsolete reports:
    # printBiomarkersByPI(portal)
    # Maureen's report:
    # printAllBiomarkers(portal)
    # Maureen's other report
    printTabularBiomarkers(portal)
    # generatePIsbyBiomaker(portal)


if __name__ == '__main__':
    # The [2:] works around plone.recipe.zope2instance-4.2.6's lame bin/interpreter script issue
    sys.exit(0 if main(sys.argv[2:]) is True else -1)
