#!/usr/bin/env python
# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Get the latest database snapshot of the Early Detection Research Network's public portal.'''

import logging, sys, getpass, os, os.path, urllib2
from optparse import OptionParser
from HTMLParser import HTMLParser

_url = 'https://edrn.nci.nih.gov/snapshots'
_logFormat = '%(asctime)s %(levelname)-8s %(message)s'
_realm = 'Database Snapshots'
_bufsiz = 1024

_op = OptionParser(usage='%prog [options] [URL]', version='0.0.0', description='Gets the latest EDRN DB snapshot')
_op.add_option('-u', '--user', dest='user', metavar='USER', default='snapshots', help='Log in with USER (default "snapshots")')
_op.add_option('-p', '--password', dest='password', metavar='PASSWORD', help='Use PASSWORD to authenticate')
_op.add_option('-d', '--dir', dest='directory', metavar='DIR', default='snapshot', help='Write to DIR (default "snapshot")')
_op.add_option('-q', '--quiet', action='store_true', default=False, dest='quiet', help='Be quiet, defaults to chatty')

class FileFinder(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self) # please use newstyle classes ffs
        self.fileLinks = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs = dict(attrs)
            link = attrs.get('href', None)
            if link and link != '/':
                self.fileLinks.append(link)
                

def buildOpener(url, user, password):
    auth = urllib2.HTTPBasicAuthHandler()
    auth.add_password(_realm, url, user, password)
    return urllib2.build_opener(auth)


def grab(url, user, password, target):
    con = None
    try:
        logging.info('Getting index of "%s"', url)
        opener = buildOpener(url, user, password)
        con = opener.open(url)
        fileFinder = FileFinder()
        fileFinder.feed(con.read())
        con.close()
        logging.info('Found %d files to download as part of the snapshot', len(fileFinder.fileLinks))
        for fn in fileFinder.fileLinks:
            src = dst = None
            try:
                srcURL, targetFile = url + '/' + fn, os.path.join(target, fn)
                logging.info('Copying "%s" to "%s"', srcURL, targetFile)
                opener = buildOpener(srcURL, user, password)
                src, dst = opener.open(srcURL), open(targetFile, 'wb')
                while True:
                    buf = src.read(_bufsiz)
                    if buf == '': break
                    dst.write(buf)
            finally:
                for stream in src, dst:
                    try:
                        stream.close()
                    except:
                        pass
        logging.info('Done.')
    finally:
        try:
            con.close()
        except:
            pass


def main(argv):
    options, args = _op.parse_args(argv)
    if len(args) > 2:
        _op.error('Specify an (optional) URL for the database snapshot.')
    elif len(args) == 2:
        url = args[1]
    else:
        url = _url
    if options.quiet:
        logging.basicConfig(level=logging.WARNING, format=_logFormat)
    else:
        logging.basicConfig(level=logging.INFO, format=_logFormat)
    if options.password:
        password = options.password
    else:
        password = getpass.getpass()
    target, user = options.directory, options.user
    if os.path.exists(target) and not os.path.isdir(target):
        logging.critical('"%s" already exists and is not a directory; not overwriting it', target)
        sys.exit(1)
    if not os.path.exists(target):
        os.makedirs(target)
    if len(os.listdir(target)) > 0:
        logging.critical('"%s" already has some files in it; cowardly refusing to use it', target)
        sys.exit(1)
    grab(url, user, password, target)

if __name__ == '__main__':
    main(sys.argv)