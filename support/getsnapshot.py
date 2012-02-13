#!/usr/bin/env python
# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Get the latest database snapshot of the Early Detection Research Network's public portal.'''

import logging, sys, getpass, os, os.path, urllib2, urlparse, base64
from optparse import OptionParser
from HTMLParser import HTMLParser

_baseURL = 'https://edrn.nci.nih.gov/'
_logFormat = '%(asctime)s %(levelname)-8s %(message)s'
_bufsiz = 1024

_op = OptionParser(usage='%prog [options] [BASEURL]', version='0.0.0', description='Gets the latest EDRN DB snapshot')
_op.add_option('-u', '--user', dest='user', metavar='USER', default='snapshots', help='Log in with USER (default "snapshots")')
_op.add_option('-p', '--password', dest='password', metavar='PASSWORD', help='Use PASSWORD to authenticate')
_op.add_option('-d', '--dir', dest='directory', metavar='DIR', default='var', help='Write to DIR (default "var")')
_op.add_option('-q', '--quiet', action='store_true', default=False, dest='quiet', help='Be quiet, defaults to chatty')

class FileFinder(HTMLParser):
    '''Parser for an Apache index page, gathering all links to files and subdirectories.'''
    def __init__(self, url):
        HTMLParser.__init__(self) # please use newstyle classes ffs
        self.fileLinks, self.dirLinks = [], []
        self.basePath = self._getParent(urlparse.urlparse(url).path)
        if not self.basePath.endswith('/'):
            self.basePath += '/'
    def _getParent(self, path):
        '''Get the parent of a url path that identifies a directory:
        
        * /x/y/z/ → /x/y/
        * /x/y/ → /x/
        * /x/ → /
        * / → /'''
        parent = '/'.join(path.split('/')[:-2])
        return parent if parent else '/'
    def handle_starttag(self, tag, attrs):
        '''Just look at anchor elements with href attributes.'''
        if tag == 'a':
            attrs = dict(attrs)
            link = attrs.get('href', None)
            if link:
                if link.endswith('/'):
                    if link != self.basePath:
                        self.dirLinks.append(link[:-1])
                else:
                    self.fileLinks.append(link)
                

def openConnection(url, user, password):
    request = urllib2.Request(url)
    authString = base64.encodestring('%s:%s\n' % (user, password)).replace('\n', '')
    request.add_header('Authorization', 'Basic %s' % authString)
    return urllib2.urlopen(request)


def grab(url, user, password, target):
    con = None
    try:
        logging.info('Getting index of "%s"', url)
        con = openConnection(url, user, password)
        fileFinder = FileFinder(url)
        fileFinder.feed(con.read())
        con.close()
        logging.info('Files: %d; directories: %d', len(fileFinder.fileLinks), len(fileFinder.dirLinks))
        for fn in fileFinder.fileLinks:
            src = dst = None
            try:
                srcURL, targetFile = url + fn, os.path.join(target, fn)
                src, dst = openConnection(srcURL, user, password), open(targetFile, 'wb')
                logging.info('Copying "%s" to "%s" of size %s', srcURL, targetFile, src.info().get('Content-length', 'UNKNOWN'))
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
        for dn in fileFinder.dirLinks:
            sub = os.path.join(target, dn)
            if not os.path.exists(sub):
                os.makedirs(sub)
            grab(url + dn + '/', user, password, sub)
        logging.info('Done.')
    finally:
        try:
            con.close()
        except:
            pass


def main(argv):
    options, args = _op.parse_args(argv)
    if len(args) > 2:
        _op.error('Specify an (optional) base URL for the database snapshot.')
    elif len(args) == 2:
        baseURL = args[1]
    else:
        baseURL = _baseURL
    if options.quiet:
        logging.basicConfig(level=logging.WARNING, format=_logFormat)
    else:
        logging.basicConfig(level=logging.INFO, format=_logFormat)
    if not baseURL.endswith('/'):
        logging.notice('Adding a "/" to base URL "%s"' % baseURL)
        baseURL += '/'
    if options.password:
        password = options.password
    else:
        password = getpass.getpass()
    target, user = options.directory, options.user
    if os.path.exists(target) and not os.path.isdir(target):
        logging.critical('"%s" already exists and is not a directory; not overwriting it', target)
        sys.exit(1)
    for dirname in ('snapshots', 'blobstorage'):
        d = os.path.join(target, dirname)
        if not os.path.exists(d):
            os.makedirs(d)
        grab(baseURL + dirname + '/', user, password, d)


if __name__ == '__main__':
    main(sys.argv)
    
