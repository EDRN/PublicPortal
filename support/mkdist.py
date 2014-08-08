#!/usr/bin/env python
# encoding: utf-8
#
# Copyright 2011–2013 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

import optparse, logging, sys, os, shutil, tempfile, atexit, urllib2, tarfile, base64, bz2

_python = 'http://python.org/ftp/python/2.7.6/Python-2.7.6.tgz'

_optParser = optparse.OptionParser(description='''Make a distribution of the EDRN portal.''', usage='%prog [options] VERSION')
_optParser.add_option('-u', '--url', default=_python, help='Override default URL to a Python 2.7 bzip2/gzip tarball.')

_distItems = (
    'bootstrap.py',
    'CHANGES.txt',
    'deploy.py',
    'egg-cache',
    'etc',
    'INSTALL.rst',
    'operations.cfg',
    'README.rst',
    'support',
    'templates',
    'versions',
)

logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

def _checkCWD():
    logging.info('Checking ')
    sentinel = os.path.abspath('operations.cfg')
    if not os.path.exists(sentinel):
        raise IOError('Distribution file "operations.cfg" not found in current directory; is CWD correct?')

def _cleanOldDist(distname):
    dists = [os.path.abspath(os.path.join('dist', distname + i)) for i in ('', '.tar.bz2')]
    for dist in dists:
        if os.path.exists(dist):
            logging.info('Deleting old distribution at %s', dist)
            if os.path.isfile(dist):
                os.remove(dist)
            else:
                shutil.rmtree(dist)
    

def _makeDist():
    tmp = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, tmp, True)
    logging.info('Copying distribution items to %s', tmp)
    for item in _distItems:
        logging.info('Copying %s', item)
        itemSrc = os.path.abspath(item)
        if os.path.isfile(itemSrc):
            shutil.copy(itemSrc, tmp)
        else:
            shutil.copytree(itemSrc, os.path.join(tmp, item), symlinks=True,
                ignore=shutil.ignore_patterns('[0-9A-Fa-f]*.0', 'mkdist.py', 'int', '.svn', 'deploy.py'))
    return tmp

def _patchDeployer(staging, version):
    srcname, destname = os.path.abspath('deploy.py'), os.path.join(staging, 'deploy.py')
    src, dest = open(srcname, 'r'), open(destname, 'w')
    for i in src:
        if i.startswith('_version ='):
            dest.write("_version = '%s'\n" % version)
        else:
            dest.write(i)
    src.close()
    dest.close()


def _installPython(staging, url):
    tmp = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, tmp, True)
    logging.info('Downloading %s', url)
    c = urllib2.urlopen(url)
    o = open(os.path.join(tmp, 'python.tar'), 'wb')
    while True:
        buf = c.read(4096)
        if buf == '': break
        o.write(buf)
    c.close()
    o.close()
    logging.info('Extracting members')
    t = tarfile.open(os.path.join(tmp, 'python.tar'))
    t.extractall(tmp)
    t.close()
    os.remove(os.path.join(tmp, 'python.tar'))
    logging.info('Pruning')
    extracteddir = [i for i in os.listdir(tmp) if os.path.isdir(os.path.join(tmp, i))][0]
    extraction = os.path.join(tmp, extracteddir)
    for i in ('Demo', 'RISCOS', 'PC', 'PCbuild', 'README'):
        prunable = os.path.join(extraction, i)
        if os.path.isfile(prunable):
            os.remove(prunable)
        else:
            shutil.rmtree(prunable)
    logging.info('Archiving')
    t = tarfile.open(os.path.join(tmp, 'pruned.tar'), 'w')
    t.add(extraction, 'in')
    t.close()
    t, e = open(os.path.join(tmp, 'pruned.tar'), 'rb'), open(os.path.join(tmp, 'pruned.tar.b64'), 'w')
    logging.info('Encoding')
    base64.encode(t, e)
    t.close()
    e.close()
    logging.info('Compressing')
    s, d = open(os.path.join(tmp, 'pruned.tar.b64'), 'r'), bz2.BZ2File(os.path.join(tmp, 'in.dat'), 'w', 4096)
    while True:
        buf = s.read(76)
        if buf == '': break
        d.write(buf)
    s.close()
    d.close()
    logging.info('Placing into staging area')
    finaldest = os.path.join(staging, 'deps')
    os.makedirs(finaldest)
    shutil.move(os.path.join(tmp, 'in.dat'), finaldest)


def _mkArchive(staging, distname):
    finaldest = os.path.join('dist')
    if not os.path.isdir(finaldest): os.makedirs(finaldest)
    finaltarget = os.path.join(finaldest, distname + '.tar.bz2')
    logging.info('Creating distribution %s', finaltarget)
    target = tarfile.open(finaltarget, 'w:bz2')
    target.add(staging, distname)
    target.close()

def main(argv):
    try:
        options, args = _optParser.parse_args(argv)
        if len(args) != 2:
            _optParser.error('Specify the VERSION of the portal whose distribution to generate, such as "4.1.0"')
        version = args[1]
        distname = 'edrn-portal-%s' % version
        _checkCWD()
        _cleanOldDist(distname)
        staging = _makeDist()
        _patchDeployer(staging, version)
        _installPython(staging, options.url)
        _mkArchive(staging, distname)
        logging.info('COMPLETE')
    except Exception, ex:
        logging.exception('Distribution failed: %s', str(ex))
        return False
    return True

if __name__ == '__main__':
    rc = main(sys.argv)
    if rc: sys.exit(0)
    else: sys.exit(-1)
