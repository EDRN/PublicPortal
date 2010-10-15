#!/bin/sh
#
# Rebuild from scratch, for developers.

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
This will shutdown the supervisord; wipe out the database, log files, etc.;
rebuild the instance; and repopulate the site content.  It'll then start the
supervisord.  You have 5 seconds to abort.
EOF
sleep 5
[ -x bin/supervisorctl ] && echo 'Shutting down supervisor...' && bin/supervisorctl shutdown
set -e
[ -d var ] && echo 'Nuking var directory...\c' && rm -r var && echo done
echo 'Nuking select parts...' && rm -rf parts/zeoserver parts/instance-debug
echo 'Remaking select parts...' && bin/buildout -c dev.cfg install zeoserver instance-debug
echo 'Populating content...' && bin/buildout -c dev.cfg install edrnsite
echo 'Starting supervisor...\c' && bin/supervisord
exit 0
