#!/bin/sh
#
# Rebuild from scratch, for developers.

snapshot=snapshot-20101006
snapshotURL=http://cancer.jpl.nasa.gov/static/edrn-portal-snapshots/${snapshot}.tar.bz2

if [ $# -ne 0 ]; then
    echo Usage: `basename $0` 1>&2
    echo "(This program takes no arguments.)" 1>&2
    exit 1
fi

if [ ! -f base.cfg -o ! -f build.cfg -o ! -f dev.cfg ]; then
    echo Run this from the buildout directory. 1>&2
    echo There should be base.cfg, build.cfg, dev.cfg files 1>&2 
    echo "(as well as any/many buildout-generated artifacts)." 1>&2
    exit 1
fi
cat <<EOF
This will shutdown the supervisord; wipe out the database, log files, etc.; copy an existing database from a snapshot backup from the operational site  It'll then start
the supervisord.  You have 5 seconds to abort.
EOF

sleep 5
numZeos=0
[ -x bin/supervisorctl ] && echo 'Shutting down supervisor...' && bin/supervisorctl shutdown && sleep 3

numZeos=`ps auxww | egrep -c '[z]eoserver'`
if [ $numZeos -ge 1 ]; then
    cat <<EOF
Warning: There are still zeoserver processes still running on this host even
after shutting down the supervisor.  They may conflict with populating the
site's content, or they may be unrelated to this buildout.  Regardless, I'll
continue in 10 seconds.
EOF
    echo 'Number of zeoservers found: ' $numZeos
    sleep 10
fi
[ -d var ] && echo 'Nuking database and logs...\c' && rm -rf var/blobstorage var/filestorage var/log && echo done
echo 'Nuking select parts...\c' && rm -rf parts/zeoserver parts/instance-debug && echo done
echo 'Remaking select parts...' && bin/buildout -c dev.cfg install zeoserver instance-debug
if [ \! -d "var/$snapshot" ]; then
    echo "Downloading $snapshot..."
    curl -L "$snapshotURL" | tar -C var -xjf -
fi
echo 'Extracting operations database...' && bin/repozo -v -R -r var/$snapshot -o var/filestorage/Data.fs
echo 'Starting supervisor...' && bin/supervisord && sleep 3
zeoRunning=`bin/supervisorctl status zeo | egrep -c RUNNING`
if [ $zeoRunning -ne 1 ]; then
    echo "The supervisor failed to start the zeo database server. I'm stuck." 1>&2
    echo "Try running bin/supervisorctl and see if you can figure out why it's broken." 1>&2
    exit 1
fi
echo 'Adding an admin user (with password "admin")...'
bin/instance-debug adduser admin admin 2>/dev/null
if [ $# -ne 0 ]; then
    cat 1>&2 <<EOF
Failed to add a new admin user. I'm stuck. Try running 
    bin/instance-debug adduser admin admin
yourself and figure out what went wrong.
EOF
    exit 1
fi
echo 'Upgrading portal to current version...' && bin/buildout -c dev.cfg install edrnsite
exit 0
