******************************************************
 Installing the Early Detection Research Network Site
******************************************************

.. contents::

This document tells how to install the Early Detection Research Network (EDRN)
public portal and knowledge environment, or more simply, the "EDRN portal",
version 4.4.  Preparation and installation takes two hours.


Preparation
===========

Before installing the EDRN site, you'll need to prepare the host and gather
some information.  This installation assumes the following:

For Development and Testing Tiers
---------------------------------

* You're installing this software in a new directory, not overwriting the
  current EDRN installation directory, if any.
* The Apache HTTPD configuration may be updated as needed to reverse-proxy to
  this, the new EDRN software installation.


For Operational or Production Tiers
-----------------------------------

* The Unix account running the EDRN portal, "edrn", won't be changing.
* The current EDRN installation directory is available for reading.  If it's
  not, copy one over from some other host.
* You're installing this software on the same host that currently runs
  the older EDRN portal, version 4.2.
* You're installing this software in a new directory, not overwriting the
  current EDRN installation directory.
* The Apache HTTPD configuration may be updated as needed to reverse-proxy to
  this, the new EDRN software installation.

Once the deployment process is complete, this software will become the new
EDRN portal software.  The old directory with version 4.2 may then be removed.


Dependencies
------------

This software has dependencies on several external packages:

* Python 2.4 or later plus development environment (Python.h headers, etc.).
* C/C++ compiler and "make" (to build additional software)
* JPEG_ 6B development libraries
* OpenSSL_ development libraries
* wvWare_ tools
* `PDF-to-HTML`_ tools
* SASL_
* OpenLDAP_
* Varnish_ version 3

NOTE: We now require Varnish 3; previously Varnish 2 was necessary.

Check and install these dependencies using your system provided tools (such as
Pirut, Aptitude, etc.) or by building and installing from source.

You'll also need a private key and public certificate for HTTPS access to the
website.


Deploying the EDRN Portal
=========================

To deploy this version of the EDRN portal, perform the following steps:

1.  Cancel the current system services (log rotation, cron jobs) for the old
    version 4.2 of the portal, if any.
2.  Run the deploy script for the new portal, version 4.4.
3.  Stop the old portal 4.2 (if any) and update its init.d startup script for
    the new version 4.4.
4.  Start the new version 4.4 processes.
5.  Adjust the Apache HTTP reverse proxy configuration and install the SSL
    certificates.
6.  Make the site.cfg file readable only by user "edrn".
7.  Install the log rotation and cron jobs for the new version 4.4 portal.

The rest of this document details the above steps.


Canceling the Current System Services
-------------------------------------

The old version of the EDRN portal currently running takes advantage of a few
operating system services, including log file rotation and periodic cron jobs.
These need to be canceled.  To do so, remove the following files/symlinks:

* /etc/cron.hourly/edrn (might be named "edrn-perms")
* /etc/cron.daily/edrn (might be named "backup" or "edrn-backup")
* /etc/cron.weekly/edrn (might be named "edrn-maint")
* /etc/cron.monthly/edrn (might be named "zeopack" or "edrn-pack")
* /etc/logrotate.d/edrn (might be named "edrn-portal")


Running the Deploy Script
-------------------------

Deploying the new version of the EDRN portal is easier than ever before.  To
do so:

1.  Extract the software archive::

        tar xjf edrn-portal-VERSION.tar.bz2
        
    Replace VERSION with the version number being deployed.  Do *not* extract
    the file over an existing installation directory; as a sibling directory,
    or elsewhere, is fine.  Do so as the EDRN user "edrn".

2.  Change the current working directory to the newly extracted directory,
    which from here on out we'll call $INSTALL_DIR::

        cd edrn-portal-VERSION

3.  Run the deployment script.  For *development and testing tiers*, type::

        ./deploy.py PUBLIC-HOSTNAME
        
    Replace PUBLIC-HOSTNAME with edrn-dev.nci.nih.gov (for development tier),
    edrn-test.nci.nih.gov (for the testing tier), or whatever else you
    require.  For example::

        ./deploy.py edrn-test.nci.nih.gov

    For *operational/production tiers*, instead type::

         ./deploy.py --existing-install=OLDPORTAL PUBLIC-HOSTNAME

    Replace OLDPORTAL with the path to the old, currently running EDRN portal.
    Replace PUBLIC-HOSTNAME with edrn.nci.nih.gov (or whatever is required).
    For example::
    
        ./deploy.py --existing-install=/home/edrn/edrn-portal-4.2.0 edrn.nci.nih.gov

The deployment script will check dependencies and system configuration, download
the EDRN portal software and its related packages, and configure them
automatically.  For operational installations, it will also copy the old content
database and upgrade it.

The deployment script will also create a detailed log file, ``deploy.log``,
with lots of information that can be helpful if anything goes wrong.  You
won't need to redirect or save the console output of the command at all.

For finer control over what the deployment script does, you can specify
additional command-line arguments.  Run ``./deploy.py --help`` for a list of
options.

If the script fails to run, try running it with the Python interpreter; i.e.::

    /usr/bin/python ./deploy.py --existing-install=/home/edrn/edrn-portal-4.2.0 edrn.nci.nih.gov

All of the steps that the script carries out can take an *enormous* amount of
time.  If you're fond of food, now would be a great time to take a lunch
break; be sure to get cocktails, appetizers, a bottle of wine, dessert, and
coffee.  Yes, it's going to be that long.


Deployment Options
~~~~~~~~~~~~~~~~~~

There's one required command-line argument for the "deploy.py" script: the
public hostname of the website.

The full set of command-line options you can provide to the ``deploy.py`` script
includes:

-e EXISTING_INSTALL, --existing-install=EXISTING_INSTALL
    This option is *required* for production/operational installlations.  Tells
    the deployment script to use the old, existing installation of the EDRN
    portal software in the directory EXISTING_INSTALL.
-s SUPERVISOR_USER, --supervisor-user=SUPERVISOR_USER
    Username to use for the process Supervisor (default "supervisor")
-x SUPERVISOR_PASSWORD, --supervisor-password=SUPERVISOR_PASSWORD
    Password for Supervisor (will be generated if not given)
-z ZOPE_USER, --zope-user=ZOPE_USER
    Username for the Zope appserver (default "edrn-admin")
-p ZOPE_PASSWORD, --zope-password=ZOPE_PASSWORD
    Password for the Zope appserver (will be generated if not given)

The remaining options control the TCP ports on which the various processes
that comprise the EDRN portal listen.  You can specify a base port number (and
each process listens on a port number offset from the base), and/or individual
port numbers.

--base-port=BASE_PORT
    Base port (procs get base +1,+2,..., default 6310)
--cache-control=NUM
    Cache control port (default base+1)
--cache-port=NUM
    Cache port (default base+2)
--supervisor-port=NUM
    Supervisor port (default base+3)
--zeo-monitor-port=NUM
    ZEO monitor port (default base+4)
--zeo-port=NUM
    ZEO database port (default base+5)
--zope-debug-port=NUM
    Zope debug port (default base+6)
--zope1-port=NUM
    Zope appserver 1 (default base+7)
--zope2-port=NUM
    Zope appserver 2 (default base+8)


Shutting Down the Old One and Starting the New One
--------------------------------------------------

After running the "deploy.py" script, you're ready to start the new EDRN portal.

First, stop any older EDRN 4.2 portal site by running the rc script as follows::

    sudo /etc/init.d/edrn-supervisor stop
    
Adjust the path to the rc script as necessary.  Then, edit the script and
replace paths to the 4.2 version with the 4.4 version.  Finally, start the new
version::

    sudo /etc/init.d/edrn-supervisor start

At this point, you can run $INSTALL_DIR/bin/supervisorctl to ensure the
various processes that provide the EDRN site are OK.  All of the following
processes should be listed as running:

============== =========================================================
Process ID     Description
============== =========================================================
``cache``      Varnish reverse proxy caching engine
``instance1``  First Zope application server
``instance2``  Second Zope application server
``zeo``        Zope Enterprise Objects database server
============== =========================================================

You can check that the site is active by fetching the following URLs
(adjusting port numbers as needed):

* http://localhost:6317/edrn (via the first Zope app server)
* http://localhost:6318/edrn (via the second Zope app server)
* http://localhost:6312/edrn (via the Varnish cache)

You should get an identical web page from all three URLs.

Onto Apache...


Front End Web Server
--------------------

The Apache HTTPD web server must now be configured.  On most NCI web systems,
Apache is already configured for EDRN, and all that is necessary is to update
the configuration with filesystem paths to the new installation directory
(typically /home/edrn/edrn-portal-4.4.X) and any new reverse-proxy TCP ports.

You'll also want to double check the SSL certificates for both HTTPS access to
the EDRN site.

The ``deploy.py`` script generated two Apache HTTPD configuration files that you
can use an examples:

* $INSTALL_DIR/ops/apache-httpd.conf
* $INSTALL_DIR/ops/apache-httpd-ssl.conf

Ultimately, you should be able to visit the following URLs with a browser:

* http://PUBLIC-HOSTNAME/
* https://PUBLIC-HOSTNAME/
* https://PUBLIC-HOSTNAME/logs (should require a password)
* https://PUBLIC-HOSTNAME/snapshots (should require a password)
* https://PUBLIC-HOSTNAME/blobstorage (should require a password)

Replace PUBLIC-HOSTNAME with the command-line argument given to the
``deploy.py`` script.


Hooking into the Operating System
---------------------------------

The EDRN site relies on services provided by the Unix operating system for its
operation.  Specifically, it needs help from Unix ...

* Via cron_, to run periodic maintenance
* Via logrotate_, to trim and archive log files


Cron Jobs
~~~~~~~~~

The EDRN site relies on the Unix cron scheduler for periodic tasks, such as
database backups and content refreshing.

To set up the cron jobs, first delete any old EDRN scripts from
/etc/cron.hourly, /etc/cron.daily, /etc/cron.weekly, and /etc/cron.monthly.
Then run::

    install -o root -g root -m 755 $INSTALL_DIR/ops/cron.daily /etc/cron.daily/edrn
    install -o root -g root -m 755 $INSTALL_DIR/ops/cron.hourly /etc/cron.hourly/edrn

EDRN no longer uses any weekly or monthly cron jobs.


Log Rotation
~~~~~~~~~~~~

During the buildout, a configuration file compatible with logrotate_ was
generated and placed in ``ops/logrotate.conf``.  First, delete any old EDRN
logrotate files, then run::

    install -o root -g root -m 644 $INSTALL_DIR/ops/logrotate.conf /etc/logrotate.d/edrn


Protecting the site.cfg file
----------------------------

Three files contain the Zope manager username and password and must be
protected::

    chmod 600 $INSTALL_DIR/site.cfg
    chmod 700 $INSTALL_DIR/ops/cron.daily
    chmod 700 /etc/cron.daily/edrn


Security Scans
--------------

Before unleashing IBM Rational AppScan or other web application scanning
technology on the site, you should make a backup of the content and settings
databases with a command similar to::

    tar cjf backup.tar.bz2 $INSTALL_DIR/var/blobstorage $INSTALL_DIR/var/filestorage

This backup can be made while the site is running.

Note that the scan should be configured to avoid certain URLs:

* Any URL that contains "selectViewTemplate"
* Any URL that ends with "@@manage-viewlets"
* Any URL that contains "@@faceted_settings"
* Any URL that ends with "object_cut"
* Any URL that ends with "delete_confirmation"
* Any URL that contains "@@faceted_subtyper"
* Any URL that contains "@@faceted_layout"
* Any URL that ends with "@@skins-controlpanel"
* Any URL that ends with "@@usergroup-userprefs"
* Any URL that contains "folder_listing".

Also, it should not click certain form controls:

* Any input type of "submit" with value "folder_cut:method"
* Any input type of "submit" with value "folder_delete:method"


Updating DNS
------------

The last step in deploying the EDRN site is to update your domain name
servers, or DNS_.  Set the CNAME for the PUBLIC-HOSTNAME appropriately.


Questions, Bug Reports, and Help
================================

For feedback about this product, please visit the feedback page at
http://cancer.jpl.nasa.gov/contact-info.


.. References:
.. _APT: http://en.wikipedia.org/wiki/Advanced_Packaging_Tool
.. _Buildout: http://www.buildout.org/
.. _CNAME: http://en.wikipedia.org/wiki/CNAME_record
.. _cron: http://en.wikipedia.org/wiki/Cron
.. _Debian: http://www.debian.org/
.. _DNS: http://en.wikipedia.org/wiki/Domain_Name_System
.. _FreeBSD: http://www.freebsd.org/
.. _GCC: http://gcc.gnu.org/
.. _logrotate: http://linuxers.org/howto/howto-use-logrotate-manage-log-files
.. _Plone: http://plone.org/
.. _Postfix: http://www.postfix.org/
.. _RHEL: http://www.redhat.com/rhel/
.. _Supervisor: http://supervisord.org/
.. _SUSE: http://www.novell.com/linux/
.. _Xcode: http://developer.apple.com/technologies/tools/xcode.html
.. _Zope: http://zope2.zope.org/
.. _virtualenv: http://www.virtualenv.org/
.. _`GNU Make`: http://www.gnu.org/software/make/
.. _`Mac OS X`: http://www.apple.com/macosx/
.. _`Python Source`: http://python.org/download/releases/2.4.6
.. _JPEG: http://www.ijg.org/
.. _OpenSSL: http://www.openssl.org/
.. _wvWare: http://wvware.sourceforge.net/
.. _pdf-to-html: http://poppler.freedesktop.org/releases.html
.. _SASL: http://asg.web.cmu.edu/sasl/
.. _OpenLDAP: http://asg.web.cmu.edu/sasl/
.. _Varnish: https://www.varnish-cache.org/


.. Author:
    Sean Kelly
    Jet Propulsion Laboratory
    California Institute of Technology

.. Copyright:
    U.S. Government sponsorship acknowledged.

