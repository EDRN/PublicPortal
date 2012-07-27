# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.
#
# Other miscellaneous cleanup

from transaction import commit
from Products.CMFCore.utils import getToolByName
import sys

def main(app):
    try:
        portal = app['edrn']
        # Die.
        portal.manage_delObjects('specimens')
        # Get rid of some packages
        qi = getToolByName(portal, 'portal_quickinstaller')
        qi.uninstallProducts(['eke.specimens'])
        # Done
        commit()
        app._p_jar.sync()
        return True
    except:
        return False


if __name__ == '__main__':
    rc = main(app) # ``app`` comes from ``instance run`` magic.
    sys.exit(0 if rc else -1)

