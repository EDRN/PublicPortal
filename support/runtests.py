# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.
#
# Run EDRN Public Portal tests

import subprocess, os, os.path, sys, ConfigParser

_executable = os.path.join('bin', 'instance-debug')
_logDir = os.path.join('var', 'testlogs')

def forciblyClose(f):
    '''Force file-like object ``f`` to close, ignoring any failure of if it's None.'''
    try:
        f.close()
    except (IOError, AttributeError):
        pass

def runTests(package):
    '''Run tests in the named package.'''
    outlog = errlog = None
    try:
        outlog = open(os.path.join(_logDir, '%s.out.log' % package), 'w')
        errlog = open(os.path.join(_logDir, '%s.err.log' % package), 'w')
        proc = subprocess.Popen(
            ('instance-debug', 'test', '-s', package),
            executable=_executable,
            stdout=outlog,
            stderr=errlog
        )
        return proc.wait() == 0
    finally:
        forciblyClose(outlog)
        forciblyClose(errlog)

def main():
    '''Run all the tests.'''
    if not os.path.isdir(_logDir):
        os.makedirs(_logDir)
    success = True
    parser = ConfigParser.SafeConfigParser()
    parser.read(['sources.cfg'])
    for package in [i[0] for i in parser.items('sources')]:
        sys.stderr.write('Running tests in "%s" ... ' % package)
        sys.stderr.flush()
        rc = runTests(package)
        success &= rc
        sys.stderr.write('%s\n' % (rc and 'pass' or 'FAIL'))
        sys.stderr.flush()
    sys.exit(success and 0 or 1)

if __name__ == '__main__':
    main()