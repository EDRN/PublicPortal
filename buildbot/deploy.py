#!/usr/bin/env python
# encoding: utf-8
# Copyright 2009-2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.
#
# Deploy the test portal to the test project site

import sys, subprocess, os, os.path, shutil

def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 3:
        print >>sys.stderr, 'Usage: %s project-base-dir python-exec' % sys.argv[0]
    basedir, executable = sys.argv[1:3]
    
    # Shut down supervisor, ignoring errors
    supervisorctl = os.path.join(basedir, 'bin', 'supervisorctl')
    if os.path.isfile(supervisorctl):
        subprocess.call((os.path.join(basedir, 'bin', 'supervisorctl'), 'shutdown'))

    # Clean out all generated files
    for f in ((os.path.join(basedir, '.installed.cfg'), os.path.join(basedir, 'var', 'known-good-versions.cfg'))):
        if os.path.exists(f):
            os.remove(f)
    for dirname in ('bin', 'develop-eggs', 'fake-eggs', 'parts', 'var'):
        shutil.rmtree(os.path.join(basedir, dirname), ignore_errors=True)
    
    # Update app server config from svn
    subprocess.call(('svn', 'up'))
    
    # Bootstrap
    subprocess.call((executable, os.path.join(basedir, 'bootstrap.py'), '-dc', os.path.join(basedir, 'buildbot.cfg')))
    
    # Buildout
    subprocess.call((os.path.join(basedir, 'bin', 'buildout'), '-c', os.path.join(basedir, 'buildbot.cfg')))
    
    # Check out source code from HEAD
    subprocess.call((os.path.join(basedir, 'bin', 'develop'), 'up'))
    
    # Re-buildout with latest source
    subprocess.call((os.path.join(basedir, 'bin', 'buildout'), '-c', os.path.join(basedir, 'buildbot.cfg')))

    # Install portal
    subprocess.call((os.path.join(basedir, 'bin', 'buildout'), '-c', os.path.join(basedir, 'buildbot.cfg'),
        'install', 'edrnsite'))
    
    # Start supervisor (which starts zeo database and zope app server)
    subprocess.call((os.path.join(basedir, 'bin', 'supervisord')))

    # Done!
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))