#!/usr/bin/env python
#
# Copyright 2011-2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

_version = 'UNKNOWN'

import sys, os, os.path, re, logging, tempfile, atexit, shutil, subprocess, optparse, string, random, pwd
try:
    import bz2 as _
    tmp = __import__('bz2', globals(), locals(), ['BZ2File'])
    Midwife = tmp.BZ2File
    import base64 as __
except ImportError:
    print >>sys.stderr, 'FATAL ERROR: cannot import bz2.'
    print >>sys.stderr, 'This version of Python (%s) does not built with libz support.' % sys.executable
    print >>sys.stderr, "Sadly, there's no way I can proceed without with now."
    sys.exit(-2)
import stat as ___
import platform as plat

# important
BUILDOUT_CHECKSUM_MD5_HASH = '1.6.3'

# previous values: edrnadmin, edrn-admin
_defZope = 'manager-edrn' # Change this each release, in case TerpSys doesn't and they re-use the uid+passwd
_defSuper = 'supervisor'
_eviOutInc = 'deploy.log'
_cHeader = '''#ifdef __cplusplus
extern "C"
#endif
'''
_checksumFile = 'operations.cfg'
_STDC = 0x1096000L
_STDC_FLAG = 4094
_ALTC_FLAG = 4093
_flags = [0x2e, 0x2f, 0x63, 0x6f, 0x6e, 0x66, 0x69, 0x67, 0x75, 0x72, 0x65]
_dn = open('/dev/null', 'rb')
_post = 'CFLAGS=-fPIC'
_bin = [0x2d, 0x34, 0x5c, 0x2e, 0x30]
_base = 6310
_pence = (055, 063, 056, 060)
_optParser = optparse.OptionParser(version=_version, description='''Deploys the EDRN portal in this directory.  This program
will download and configure the EDRN software and dependencies.  It will then extract the old, existing portal's database,
upgrade it to the structure for this, the new version, and prepare it for operations.  See the README.txt for more details.''',
usage='Usage: %prog [options] PUBLIC-HOSTNAME')
_optParser.add_option('-e', '--existing-install', help='Path to the old pre-existing installation of EDRN portal. Required.')
_optParser.add_option('-s', '--supervisor-user', default=_defSuper, help='Username to use for Supervisor (default "%default")')
_optParser.add_option('-x', '--supervisor-password', help='Password for Supervisor (will be generated if not given)')
_zopeGroup = optparse.OptionGroup(_optParser, 'Zope Options', '''Note that all existing Zope admin users will be erased.
A single new Zope admin user will be created.''')
_zopeGroup.add_option('-z', '--zope-user', default=_defZope, help='Username for the Zope appserver (default "%default")')
_zopeGroup.add_option('-p', '--zope-password', help='Password for the Zope appserver (will be generated if not given)')
_optParser.add_option_group(_zopeGroup)
_portGroup = optparse.OptionGroup(_optParser, 'Port Options', '''Each process listens on a TCP port bound to localhost (save
Supervisor, which binds to all interfaces).  You can select a base port (each process gets base +1, +2, etc.) or select
ports individually.''')
_portGroup.add_option('--base-port', default=_base, type='int', help='Base port (procs get base +1,+2,..., default %default)')
_portGroup.add_option('--cache-control',    metavar='NUM', type='int', help='Cache control port (default base+1)')
_portGroup.add_option('--cache-port',       metavar='NUM', type='int', help='Cache port (default base+2)')
_portGroup.add_option('--supervisor-port',  metavar='NUM', type='int', help='Supervisor port (default base+3)')
_portGroup.add_option('--zeo-monitor-port', metavar='NUM', type='int', help='ZEO monitor port (default base+4)')
_portGroup.add_option('--zeo-port',         metavar='NUM', type='int', help='ZEO database port (default base+5)')
_portGroup.add_option('--zope-debug-port',  metavar='NUM', type='int', help='Zope debug port (default base+6)')
_portGroup.add_option('--zope1-port',       metavar='NUM', type='int', help='Zope appserver 1 (default base+7)')
_portGroup.add_option('--zope2-port',       metavar='NUM', type='int', help='Zope appserver 2 (default base+8)')
_optParser.add_option_group(_portGroup)
_workspace = None
_p = ''.join([chr(i) for i in _pence])
_logger = re.compile(''.join([chr(i) for i in _bin]))
_cfgFileMap = {
    'cache': 'cache_port',
    'cache-control': 'cache_control',
    'instance-debug': 'zope_debug_port',
    'instance1': 'zope1_port',
    'instance1-icp': 'zope1_port',
    'instance2': 'zope2_port',
    'instance2-icp': 'zope2_port',
    'supervisor': 'supervisor_port',
    'zeo-monitor': 'zeo_monitor_port',
    'zeo-server': 'zeo_port',
}


def _exec(cl, binary, cwd):
    '''Exec binary w/cl in cwd redir 2 to 1 and return seq of outlines + rc'''
    sub = subprocess.Popen(cl, _ALTC_FLAG, binary, _dn, subprocess.PIPE, subprocess.STDOUT, None, True, False, cwd, None, True)
    out, ignore = sub.communicate()
    sub.wait()
    lines = out.split('\n')
    for i in lines: logging.debug('From "%r": %s', cl, _logger.sub(_p, i))
    return lines, sub.returncode


def _setupLogging():
    '''Set up logging to two destinations:
    1. All messages down to the debug level go to the deployment log file.
    2. Messages down to the info level go to stderr
    '''
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
        filename=_eviOutInc, filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
    logging.getLogger('').addHandler(console)
    logging.debug('Logging configured')


def _checkInt():
    '''Check int'''
    logging.info('Checking...')
    fd, name = tempfile.mkstemp(suffix='.py', dir=_workspace)
    out = os.fdopen(fd, 'w')
    out.write('import sys; print sys.subversion')
    out.close()
    ipath = os.path.abspath(os.path.join('support', 'int', 'bin', 'python'))
    if not os.path.exists(ipath):
        logging.debug("ipath doesn't exist %r", ipath)
        return False
    m = os.stat(ipath)[0]
    if ___.S_ISREG(m) and ___.S_IMODE(m) & ___.S_IEXEC:
        logging.debug('ipath has isreg + imode pos iexec')
        out, rc = _exec(['python', name], ipath, os.path.abspath(_workspace))
        if rc == 0 and out[0].startswith("('CPython', 'tags"): return True
    logging.debug('ipath not useable so del')
    shutil.rmtree(os.path.abspath(os.path.join('support', 'int')), True)
    return False


def _paintTarget():
    logging.info('Painting')
    d = os.path.abspath(os.getcwd())
    while d != '/':
        try:
            logging.debug('Trying %s', d)
            os.chmod(___.S_IROTH | ___.S_IXOTH | ___.S_IXGRP | ___.S_IRGRP | ___.S_IXUSR | ___.S_IRUSR)
        except:
            pass
        d = os.path.abspath(os.path.join(d, '..'))

def _center():
    sentinel = os.path.abspath(_checksumFile)
    logging.debug('Sentinels are %r', sentinel)
    if not os.path.exists(sentinel):
        raise IOError('Distribution file "%s" not found in current directory; is CWD correct?' % _checksumFile)
    logging.debug('PID %d', os.getpid())
    if os.path.exists(sentinel):
        logging.debug('CWD %s', os.getcwd())
        logging.debug('Login %s', os.getlogin())
    else:
        logging.debug('WTF %s', os.ctermid()) # corner case


def _withdrawInt():
    '''Withdraw int'''
    global _workspace
    from tarfile import open as _open
    logging.info('Withdrawing int')
    fd, midwife = tempfile.mkstemp(dir=_workspace)
    mid = os.fdopen(fd, 'wb')
    prebirth = os.path.abspath(os.path.join('deps', 'in.dat'))
    logging.info('Prebirth %#x', os.stat(prebirth)[6])
    src = Midwife(prebirth, 'r', 4096)
    while True:
        buf = src.read(4096)
        if buf == '': break
        mid.write(buf)
    mid.close()
    src.close()
    mid = open(midwife, 'rb')
    s = os.stat(midwife)
    logging.info('Afterbirth %d, %#x', s[0], s[6])
    fd, tarwife = tempfile.mkstemp(dir=_workspace)
    target = os.fdopen(fd, 'wb')
    __.decode(mid, target)
    mid.close()
    target.close()
    mid = _open(tarwife, 'r:', None, 4097)
    mid.extractall(_workspace)
    mid.close()
    os.unlink(midwife)
    os.unlink(tarwife)

def _composeInt():
    '''Compose the int'''
    logging.info('Composing dependencies, this may take some time (over 15 minutes)')
    pre = [0x2d, 0x2d, 0x70, 0x72, 0x65, 0x66, 0x69, 0x78]
    tar = os.path.abspath(os.path.join('support', 'int'))
    vec = [''.join([chr(i) for i in _flags]), ''.join([chr(i) for i in pre]), tar, _post]
    out, rc = _exec(vec, ''.join([chr(i) for i in _flags]), os.path.abspath(os.path.join(_workspace, 'in')))
    logging.debug('RC: %d', rc)
    if rc != 0: raise OSError('C failed with return code %d' % rc)
    logging.info('Making C libs, this may take even longer')
    out, rc = _exec(['make', 'install'], _which('make'), os.path.abspath(os.path.join(_workspace, 'in')))
    logging.debug('RC: %d', rc)
    if rc != 0: raise OSError('Make failed with return code %d' % rc)
    

def _deployInt():
    '''Deploy the int'''
    global _workspace
    if _checkInt():
        logging.info('Int available')
        return
    logging.info('Deploying int')
    _withdrawInt()
    _composeInt()
    

def _easel():
    '''Create a suitable workspace'''
    global _workspace
    _workspace = os.path.abspath(os.path.join('var', 'tmp'))
    if not os.path.isdir(_workspace):
        os.makedirs(_workspace)
    atexit.register(shutil.rmtree, _workspace, True)


def _which(p):
    '''Find full path to executable p'''
    logging.debug('Which %s', p)
    def isExec(path):
        return os.path.isfile(path) and os.access(path, os.X_OK)
    path, name = os.path.split(p)
    if path:
        if isExec(p): return p
    else:
        for d in os.environ['PATH'].split(os.pathsep):
            path = os.path.join(d, p)
            if isExec(path): return path
    return None


def _showNotice():
    '''Make some informative loggings'''
    logging.info('Deploying EDRN Portal %s for %s', _version, plat.platform())
    logging.debug('Machine %s named %s processor %s', plat.machine(), plat.node(), plat.processor())
    logging.debug('Architecture %s, release %s, system %s', plat.architecture(), plat.release(), plat.system())
    logging.debug('Plat version %s', plat.version())
    if hasattr(plat, 'linux_distribution'):
        logging.debug('Linux distribution %r', plat.linux_distribution())


def _checkLib(lib, func, cc):
    '''Test for func in lib (and avail of lib)'''
    logging.info('Checking for %s in %s', func, lib)
    fd, fn = tempfile.mkstemp(suffix='.c', dir=_workspace)
    out = os.fdopen(fd, 'w')
    out.write(_cHeader)
    out.write('char %s();\nint main() {\nreturn %s();}\n' % (func, func))
    out.close()
    out, rc = _exec([cc, fn, '-l%s' % lib], _which('cc'), os.path.abspath(_workspace))
    if rc != 0: raise OSError('Could not link %s for function %s; is %s installed?' % (lib, func, lib))


def _checkDepends(): 
    '''Ensure depends are avail'''
    logging.info('Checking for make')
    if not _which('make'): raise IOError('No "make" executable found; try installing dev tools')
    logging.info('Checking for cc or gcc')
    cc, gcc = _which('cc'), _which('gcc')
    if not cc and not gcc: raise IOError('Neither "cc" nor "gcc" found; try installing dev tools')
    if gcc: cc = gcc
    logging.info('Checking for wvHtml')
    if not _which('wvHtml'): raise IOError('No "wvHtml" executable found; try installing wvWare')
    logging.info('Checking for pdftohtml')
    if not _which('pdftohtml'): raise IOError('No "pdftohtml" executable found; try installing poppler-utils')
    logging.info('Checking for varnishd')
    if not _which('varnishd'): raise IOError('No "varnishd" executable found; try installing varnish-2.1.5 or put it in PATH')
    _checkLib('jpeg', 'jpeg_read_header', cc)
    _checkLib('ssl', 'SSL_accept', cc)
    _checkLib('sasl2', 'sasl_setpass', cc)
    _checkLib('ldap', 'ldap_open', cc)


def _checkIP():
    '''Check public IP'''
    logging.info('Checking IP address')
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    if ip == '127.0.0.1':
        logging.warning('IP for host-by-name for hostname is 127.0.0.1 (localhost), but I expected a non-localhost address')
        logging.warning('This is OK for multihomed systems and might be OK in general')
    return ip


def _generatePasswd():
    '''Create a new random password'''
    chars = string.letters + string.digits
    return ''.join([random.choice(chars) for i in range(32)])


def _checkPasswd(passtype, passwd):
    '''Ensure passwd is OK for passtype'''
    # actually same restrictions
    if passwd.find(':') != -1: _optParser.error('The %s password must not contain any ":" characters.' % passtype)
    if len(passwd) > 32: _optParser.error('The %s password is too long; please limit it to 32 characters.' % passtype)
    if len(passwd) < 8: _optParser.error('The %s password is too short; please provide a decent password.' % passtype)

 
def _checkExisting(location):
    '''Make sure existing installation looks OK'''
    for fragment in (('bin', 'supervisorctl'), ('bin', 'repozo'), ('var', 'blobstorage'), ('var', 'filestorage', 'Data.fs')):
        path = os.path.abspath(os.path.join(location, *fragment))
        if not os.path.exists(path):
            raise IOError('Item "%s" not found in old, existing portal at "%s"; check --existing-install option'
                % (os.path.join(*fragment), location))


def _getLogger():
    '''Get the login id to use'''
    username = pwd.getpwuid(os.getuid())[0]
    logname = os.environ['LOGNAME']
    if logname != username:
        logging.warning("LOGNAME \"%s\" does not match current user ID's account name \"%s\", preferring latter", logname, username)
    logging.info('EDRN processes will run under Unix account "%s"', username)
    return username


def _collatePorts(options):
    '''Collate ports'''
    base = options.base_port
    index = 0
    ports = {}
    for name in ('cache_control', 'cache_port', 'supervisor_port', 'zeo_monitor_port', 'zeo_port', 'zope_debug_port',
        'zope1_port', 'zope2_port'):
        pnum = getattr(options, name)
        if not pnum:
            index += 1
            pnum = base + index
        if pnum in ports.values():
            _optParser.error('Port %d already in use; try a different number for "%s"' % (pnum, name))
        if pnum < 1024:
            _optParser.error('Port %d for "%s" requires root to run; please configure higher port numbers' % (pnum, name))
        ports[name] = pnum
    return ports


def _writeConfig(login, zopeu, zopep, superu, superp, ports, publicHostname):
    '''Generate site.cfg'''
    logging.info('Generating site.cfg')
    out = open(os.path.abspath('site.cfg'), 'w')
    print >>out, '[buildout]'
    print >>out, 'extends = operations.cfg'
    print >>out, '[hosts]'
    print >>out, 'public-hostname = %s' % publicHostname
    print >>out, '[instance-settings]'
    print >>out, 'username = %s' % zopeu
    print >>out, 'password = %s' % zopep
    print >>out, '[supervisor-settings]'
    print >>out, 'user = %s' % superu
    print >>out, 'password = %s' % superp
    print >>out, '[executables]'
    print >>out, 'varnishd = %s' % _which('varnishd')
    print >>out, '[users]'
    print >>out, 'cache = %s' % login
    print >>out, 'zeo = %s' % login
    print >>out, 'zope = %s' % login
    print >>out, '[ports]'
    for k, v in _cfgFileMap.items():
        print >>out, '%s = %d' % (k, ports[v])
    out.close()
    logging.info('Postflight %#x', os.stat(os.path.abspath('site.cfg'))[6])
    out = open(os.path.abspath('p4a.cfg'), 'w')
    print >>out, '[buildout]'
    print >>out, 'extends = site.cfg p4a-removal.cfg'
    out.close()
    logging.info('Artists %#x', os.stat(os.path.abspath('p4a.cfg'))[6])
    

def _bootstrap():
    '''Run BS.'''
    laces = os.path.abspath(os.path.join('bin', 'buildout'))
    if os.access(laces, os.X_OK):
        logging.info('Skipping bootstrap via %#x', os.stat(laces)[6])
        return
    logging.info('Bootstrapping %#x', os.stat(os.path.abspath('bootstrap.py'))[6])
    p = os.path.abspath(os.path.join('support', 'int', 'bin', 'python'))
    out, rc = _exec([p, 'bootstrap.py', '-d', '-v', BUILDOUT_CHECKSUM_MD5_HASH, '-c', os.path.abspath('site.cfg')], p, os.getcwd())
    if rc != 0: raise IOError('Bootstrap failed')


def _buildout(zopeu, zopep):
    '''Buildout.'''
    logging.info('Building out %#x, this may take a LONG time (20 mins to full hour)',
        os.stat(os.path.abspath(os.path.join('bin', 'buildout')))[6])
    out, rc = _exec(['bin/buildout', '-c', 'site.cfg'], os.path.abspath(os.path.join('bin', 'buildout')), os.getcwd())
    if rc != 0: raise IOError('Buildout failed')

def _snapshotDB(existing):
    logging.info('Snapshotting current database')
    srcdb = os.path.abspath(os.path.join(existing, 'var', 'filestorage', 'Data.fs'))
    snapshotdir = os.path.abspath(os.path.join(_workspace, 'snapshot'))
    if not os.path.isdir(snapshotdir):
        os.makedirs(snapshotdir)
    out, rc = _exec(['bin/repozo', '-B', '-v', '-F', '-r', snapshotdir, '-f', srcdb],
        os.path.abspath(os.path.join('bin', 'repozo')), os.getcwd())
    if rc != 0: raise IOError('Taking a snapshot of the existing database failed with status %d' % rc)

def _blobs(existing):
    logging.info('Amoeba')
    srcdb = os.path.abspath(os.path.join(existing, 'var', 'blobstorage'))
    logging.info('Amoeba flags %#x', os.stat(srcdb)[6])
    tar = os.path.abspath(os.path.join('var', 'blobstorage'))
    shutil.rmtree(tar, ignore_errors=True)
    shutil.copytree(srcdb, tar, True)

def _extractSnapshot(repo):
    logging.info('Extracting snapshot from %s into new operational location', repo)
    snapshotdir = os.path.abspath(os.path.join(_workspace, repo))
    fsdir = os.path.abspath(os.path.join('var', 'filestorage'))
    if not os.path.isdir(fsdir):
        os.makedirs(fsdir)
    newdb = os.path.join(fsdir, 'Data.fs')
    out, rc = _exec(['bin/repozo', '-R', '-v', '-r', snapshotdir, '-o', newdb],
        os.path.abspath(os.path.join('bin', 'repozo')), os.getcwd())
    if rc != 0: raise IOError('Restoring the database from the snapshot failed with status %d' % rc)
    logging.info('Data.fs %#x', os.stat(newdb)[6])

def _updateDatabase(zopeu, zopep):
    logging.info('Starting DB server')
    zeo = os.path.abspath(os.path.join('bin', 'zeoserver'))
    out, rc = _exec(['bin/zeoserver', 'start'], zeo, os.getcwd())
    if rc != 0: raise IOError("Couldn't start zeoserver, status %d" % rc)
    logging.info('Setting Zope user & password')
    out, rc = _exec(['bin/instance-debug', 'adduser', zopeu, zopep], os.path.abspath(os.path.join('bin', 'instance-debug')),
        os.getcwd())
    logging.info('Upgrading database to %s structure, this may take over 30 minutes', _version)
    out, rc = _exec(['bin/instance-debug', 'run', 'support/upgrade.py', zopeu, zopep],
        os.path.abspath(os.path.join('bin', 'instance-debug')), os.getcwd())
    logging.debug('Database upgrade exited with %d', rc)
    logging.info('Packing')
    out, rc = _exec(['bin/zeopack'], os.path.abspath(os.path.join('bin', 'zeopack')), os.getcwd())
    logging.info('Stopping DB server')
    out, rc = _exec(['bin/zeoserver', 'stop'], zeo, os.getcwd())

def main(argv=sys.argv):
    try:
        options, args = _optParser.parse_args(argv)
        if len(args) != 2:
            _optParser.error('Specify the public hostname of the portal, such as "edrn.nci.nih.gov", "edrn-dev.nci.nih.gov", etc.')
        publicHostname = args[1]
        if not options.existing_install:
            _optParser.error('You must indicate the location of the old, existing EDRN portal with the --existing-install option.')
        zopePasswd, superPasswd = options.zope_password, options.supervisor_password
        if not zopePasswd: zopePasswd = _generatePasswd()
        if not superPasswd: superPasswd = _generatePasswd()
        _checkPasswd('zope', zopePasswd)
        _checkPasswd('supervisor', superPasswd)
        ports = _collatePorts(options)
        _setupLogging()
        logging.debug('main')
        _checkExisting(options.existing_install)
        _center()
        _paintTarget()
        _easel()
        _showNotice()
        _checkDepends()
        ip = _checkIP()
        login = _getLogger()
        _deployInt()
        _writeConfig(login, options.zope_user, zopePasswd, options.supervisor_user, superPasswd, ports, publicHostname)
        _bootstrap()
        _buildout(options.zope_user, zopePasswd)
        _snapshotDB(options.existing_install)
        _blobs(options.existing_install)
        _extractSnapshot('snapshot')
        _updateDatabase(options.zope_user, zopePasswd)
        logging.info('DEPLOYMENT COMPLETE')
    except Exception, ex:
        logging.exception('Deployment failed: %s', str(ex))
        logging.critical('Cannot continue, sorry. Email deploy.log to edrn-ic@jpl.nasa.gov for help.')
        return False
    return True


if __name__ == '__main__':
    rc = main(sys.argv)
    if rc: sys.exit(0)
    else: sys.exit(-1)
