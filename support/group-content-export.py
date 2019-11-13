# encoding: utf-8
#
# Run this with ``bin/instance-debug run support/group-content-export.py``

from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy, OmnipotentUser
from Testing import makerequest
try:
    from zope.app.component.hooks import setSite
except ImportError:
    from zope.component.hooks import setSite
import logging, argparse, sys, os.path, os, shutil, json


app = globals().get('app', None)  # ``app`` comes from ``instance run`` magic.

_logger = logging.getLogger('group-content-export')
_logger.setLevel(logging.DEBUG)
_console = logging.StreamHandler(sys.stderr)
_formatter = logging.Formatter('%(levelname)-8s %(message)s')
_console.setFormatter(_formatter)
_logger.addHandler(_console)

# Set Up Command-line Options
# ---------------------------

_argParser = argparse.ArgumentParser(description=u'Exports group content')


# From Whence To Export
# ---------------------

_exportFrom = (
    ('collaborative-groups', 'g-i-and-other-associated-cancers-research-group'),
    ('collaborative-groups', 'breast-and-gynecologic-cancers-research-group'),
    ('collaborative-groups', 'lung-and-upper-aerodigestive-cancers-research'),
    ('collaborative-groups', 'prostate-and-urologic-cancers-research-group'),
    ('committees', 'collaboration-and-publication-subcommittee'),
    ('committees', 'data-sharing-and-informatics-subcommittee'),
    ('committees', 'network-consulting-team'),
    ('committees', 'steering-committee'),
)


# Classes
# -------

class _Exporter(object):
    def __init__(self, obj):
        self.obj = obj
    def export(self, target):
        raise NotImplementedError(u'Subclasses must implement ``export``')


class NullExporter(_Exporter):
    def export(self, target):
        _logger.debug(u'Null exporter ignoring %s', self.obj.id)


class FolderExporter(_Exporter):
    def getPloneType(self):
        return 'Folder'
    def export(self, target):
        # Ugh.
        objID = self.obj.id
        if objID == 'lung-and-upper-aerodigestive-cancers-research':
            objID = 'lung-and-upper-aerodigestive-cancers-research-group'
        d = os.path.join(target, objID)
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(os.path.join(d, 'TYPE.txt'), 'w') as f:
            f.write(self.getPloneType())
        details = {
            'title': self.obj.Title().decode('utf-8'),
            'description': self.obj.Description().decode('utf-8') if self.obj.Description() else u''
        }
        with open(os.path.join(d, 'metadata.json'), 'wb') as f:
            json.dump(details, f)
        for itemID, item in self.obj.items():
            exporter = getExporter(item)
            exporter.export(d)


class CollaborativeGroupExporter(FolderExporter):
    def getPloneType(self):
        return 'eke.knowledge.collaborativegroupfolder'


class GroupSpaceExporter(FolderExporter):
    def getPloneType(self):
        return 'eke.knowledge.groupspacefolder'


class FileExporter(_Exporter):
    def export(self, target):
        objID = self.obj.id
        d = os.path.join(target, objID)
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(os.path.join(d, 'TYPE.txt'), 'w') as f:
            f.write('File')
        details = {
            'filename': self.obj.getFilename(),
            'contentType': self.obj.getContentType(),
            'size': self.obj.get_size(),
            'title': self.obj.Title().decode('utf-8'),
            'description': self.obj.Description().decode('utf-8')
        }
        with open(os.path.join(d, 'metadata.json'), 'wb') as f:
            json.dump(details, f)
        with open(os.path.join(d, 'file.dat'), 'wb') as ooo:
            with self.obj.getFile().getBlob().open('r') as iii:
                shutil.copyfileobj(iii, ooo)


class GroupEventExporter(_Exporter):
    def export(self, target):
        d = os.path.join(target, self.obj.id)
        if not os.path.isdir(d):
            os.makedirs(d)
        # First the event
        details = {
            'title': self.obj.title,
            'description': self.obj.description,
            'location': self.obj.location,
            'startDate': self.obj.startDate.utcdatetime().isoformat(),
            'endDate': self.obj.endDate.utcdatetime().isoformat(),
            'attendees': self.obj.attendees,
            'eventUrl': self.obj.eventUrl,
            'contactName': self.obj.contactName,
            'contactEmail': self.obj.contactEmail,
            'contactPhone': self.obj.contactPhone,
            'text': self.obj.getText()
        }
        with open(os.path.join(d, 'EVENT.json'), 'wb') as f:
            json.dump(details, f)
        with open(os.path.join(d, 'TYPE.txt'), 'w') as f:
            f.write('Group Event')
        # Now its contents
        for itemID, item in self.obj.items():
            exporter = getExporter(item)
            exporter.export(d)


_exporters = {
    'Collaborative Group':       CollaborativeGroupExporter,
    'Collaborative Group Index': NullExporter,
    'File':                      FileExporter,
    'Folder':                    FolderExporter,
    'Group Event':               GroupEventExporter,
    'Group Space':               GroupSpaceExporter,
    'Group Space Index':         NullExporter,
    'Highlight':                 NullExporter,
}


# Functions
# ---------

def getExporter(obj):
    try:
        exporterClass = _exporters.get(obj.portal_type, NullExporter)
    except AttributeError:
        exporterClass = NullExporter
    return exporterClass(obj)


def setupZopeSecurity(app):
    _logger.debug('Setting up Zope security')
    acl_users = app.acl_users
    setSecurityPolicy(PermissiveSecurityPolicy())
    newSecurityManager(None, OmnipotentUser().__of__(acl_users))


def getPortal(app):
    _logger.debug('Getting portal "edrn"')
    portal = getattr(app, 'edrn')
    setSite(portal)
    return portal


def exportContent(portal, folders, exportDir):
    for containerName, groupFolderName in folders:
        if containerName:
            groupFolder = portal.unrestrictedTraverse((containerName, groupFolderName))
        else:
            groupFolder = portal.unrestrictedTraverse((groupFolderName,))
        exporter = getExporter(groupFolder)
        exporter.export(exportDir)


def exportGroupContent(app):
    _logger.info('Start export of group content')
    app = makerequest.makerequest(app)
    setupZopeSecurity(app)
    portal = getPortal(app)
    exportDir = os.path.abspath(os.path.join(os.getcwd(), 'var', 'group-export'))
    shutil.rmtree(exportDir, ignore_errors=True)
    os.makedirs(exportDir)
    exportContent(portal, _exportFrom, exportDir)
    # Wait, we aren't changing anything? Skip committing.
    # _logger.debug('Committing transactions')
    # transaction.commit()
    _logger.info('Content exported to %s', exportDir)
    _logger.debug('Withdrawing security manager')
    noSecurityManager()
    _logger.debug('All done')


def main(argv):
    args = _argParser.parse_args(argv)  # NOQA … why are we even using args?
    global app
    exportGroupContent(app)
    return True


if __name__ == '__main__':
    # The [2:] works around plone.recipe.zope2instance-4.2.6's lame bin/interpreter script issue
    sys.exit(0 if main(sys.argv[3:]) is True else -1)
