**************************************************************************
 Early Detection Research Network Public Portal and Knowledge Environment
**************************************************************************

.. contents::

Welcome to the Early Detection Research Network (EDRN) public portal and
knowledge environment.  This software package sets up various software
components that provide a functioning website for EDRN, normally hosted at
http://edrn.nci.nih.gov/.

This software was developed by and is copyrighted 2010 by the California
Institute of Technology.  ALL RIGHTS RESERVED.  U.S.  Government sponsorship
acknowledged.

The EDRN public portal is built upon a number of technologies, including:

* Buildout_ software build system
* HAProxy_ load balancer
* Nginx_ web server
* OpenSSL_ encryption toolkit
* Plone_ content management system
* Python_ programming language
* Supervisor_ process monitor
* Varnish_ caching engine
* Zope_ application server

Installation of the EDRN public portal will, in most cases, automatically
configure and deploy the above systems for you.  To install the portal, check
that your system meets the requirements listed in the Requirements section,
then follow the steps in the Installation section.


Quick Install
=============

Crave adventure and hate reading?  Skip the rest of this document and adapt
the following procedure to your environment::

    % python2.4 -V
    2.4.x
    % python2.4 -c 'import _imaging, profile'
    % locate Python.h tls1.h libssl.so
    /usr/local/include/python2.4/Python.h
    /usr/include/openssl/dtls1.h
    /usr/include/openssl/tls1.h
    /usr/lib/libssl.so
    /usr/lib/libssl.so.5
    ...
    % tar xjf ~/edrn.nci.nih.gov.tar.bz2
    % cd edrn.nci.nih.gov
    % vi operations.cfg
    % cp ~/keys/server.crt ~/keys/server.key etc
    % python2.4 bootstrap.py -dc operations.cfg
    Downloading http://pypi.python.org/packages/source/d/distribute/distribute-0.6.10.tar.gz
    ...
    Generated script '/usr/home/kelly/edrn.nci.nih.gov/bin/buildout'.
    % bin/buildout -c operations.cfg
    Installing pcre-build.
    ...
    % python2.4 support/runtests.py
    Running tests in "edrn.theme" ... pass
    ...
    % bin/buildout -c operations.cfg install edrnsite
    % sudo chown -R www parts var
    % sudo bin/supervisord
    % sudo ln -s bin/logrotate.conf /etc/logrotate.d/edrn-portal
    % curl -u supervisor-admin:password http://localhost:9001/
    ...
    % curl http://edrn.nci.nih.gov/
    ...
    % curl https://edrn.nci.nih/gov/
    ...
    % echo Miller time
    Miller time

Come back to this document if you get stuck!


Requirements
============

Before attempting to install this software, please ensure your target system
meets the prerequisite requirements detailed in this section.

In summary, these requirements are:

* A Unix-like system
* Mail server (for password reminder email, newsletter email)
* C/C++ compiler and "make" (to build additional software)
* Python 2.4 plus development environment (Python.h headers, etc.)
* Python Imaging Library installed in Python 2.4 environment
* TLS/SSL certificate for HTTPS

Details on each of these requirements are detailed in the subsections below.


Unix
----

The EDRN portal is designed to run on systems that behave like Unix systems.
We've developed and tested the portal on a variety of Unix systems, including:

* `Mac OS X`_ 10.6 "Snow Leopard", with the Xcode_ software development kit
* Debian_ GNU/Linux 5.0.3 "Lenny"
* FreeBSD_ 8.0
* SUSE_ Linux Enterprise Server 11

Other Unix systems will likely work just fine.  Windows-based systems are
*not* supported.  Make sure your Unix-like system can resolve hostnames,
including its own.  The target volume will need about 700 megabytes of free
disk space.  We recommend a full gigabyte of free space (for log file
growth).


Mail Server
-----------

The EDRN portal will need to send email messages (for password reminders and
other administrivia).  As a result, please ensure the target system runs an
SMTP server, such as Postfix_, or can access an SMTP server.  The portal is
capable of accessing SMTP servers that require user names and passwords.  See
post-deployment configuration below.


C/C++ Compilers and Make
------------------------

Although written primarily in Python, some components that comprise the EDRN
portal are written as C/C++-based Python extensions.  You'll therefore need to
make sure a C/C++ compiler (such as GCC_) as well as the ``make`` utility are
available.

*Important note for FreeBSD Users*: one component of the EDRN portal requires
the `GNU Make`_ utility.  It won't work with the system's default BSD make.
Install GNU Make from the ports ``devel`` collection, link
``/usr/local/bin/gmake`` to ``/usr/local/bin/make``, and ensure
``/usr/local/bin`` appears before ``/usr/bin`` in your execution path.


Python
------

The EDRN portal is written in the Python_ programming language and, at this
time, requires version 2.4 of Python.  Later versions, such as 2.6 and 3.0,
will *not* work.  Some operating systems provide a Python runtime environment
only.  You will need *both* the runtime *and* the development installation of
Python.

To see if you have the runtime, run ``python2.4 -V``.  You should see output
similar to ``Python 2.4.6``.  To see if you have the development environment,
check for the file ``python2.4/Python.h``.

You may build and install Python 2.4 from the `Python source`_, or consult the
following list for platform-specific versions of Python:

Debian
    Install both APT_ packages ``python2.4`` and ``python2.4-dev`` using
    ``apt-get install``, ``aptitude`` or similar utility.  See the special
    subsection on Debian GNU/Linux below.
FreeBSD
    Install ``python24`` from the ports ``lang`` section, enabling the
    HUGE_STACK_SIZE option.
Mac OS X
    Install the Python 2.4.4 package from
    http://python.org/ftp/python/2.4.4/python-2.4.4-macosx2006-10-18.dmg
SUSE
    First install ``zlib-devel`` and ``readline-devel``.  Then compile from
    `Python source`_.  Recommended configuration options are ``--enable-ipv6``
    and ``--enable-shared``.
    

Special Note on Debian GNU/Linux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Debian GNU/Linux does not include the complete Python distribution as the
Debian package maintainers feel part of Python, the Python Profiler, is *not*
free software.  The California Institute of Technology provides no opinion on
the veracity or merit of this argument.  However, the Python Profiler is
required to run the EDRN portal tests.

To install the Python Profiler on Debian GNU/Linux:

1.  Edit the ``/etc/apt/sources.list`` file and append the following two
    lines::

        deb http://ftp.us.debian.org/debian/ stable main non-free
        deb-src http://ftp.us.debian.org/debian/ stable main non-free

2.  Run ``apt-get update`` as root.

3.  Run ``apt-get install python-profiler`` as root.

You can confirm installation by running ``python 2.4 -c 'import profile'``.
The command should produce no output and exit successfully.  If you see an
error message, the Python Profiler is *not* installed.

    
Python Imaging Library
----------------------

Your Python 2.4 installation must be augmented with the Python Imaging Library
(PIL_).  PIL provides necessary features for the EDRN portal.  You can check
for PIL by running ``python2.4 -c 'import _imaging'``.  You should see no
output and successful exit status.  If you see an error message, you'll need
to install PIL.

You can install PIL from source. Or, see platform-specific notes below:

Debian
    Install the APT package ``python-imaging``.
FreeBSD
    Install ``jpeg`` and ``png`` from the ports ``graphics`` section, then
    install PIL from source.  Make sure to use ``python2.4`` to build and
    install PIL.
Mac OS X
    Install the libpng and libjpeg combo installer from
    http://ethan.tira-thompson.org/Mac_OS_X_Ports.html.  Then, install PIL
    from source.  Make sure to use
    ``/Library/Frameworks/Python.framework/Version/2.4/bin/python2.4`` to
    build and install PIL.
SUSE
    Use YaST2 to install ``libjpeg`` and ``libjpeg-devel``.  Then install PIL
    from source.  Make sure to use to ``/usr/local/bin/python2.4`` to build
    and install PIL.

If you build PIL yourself, ignore warnings about TKINTER, FREETYPE2, and
LITTLECMS support not being available.  They're not necessary.


OpenSSL
-------

The portal supports HTTPS for secure communication to protected data.  It also
uses LDAPS in order to authenticate users.  Therefore, it requires that
OpenSSL_ is installed, including both the runtime and development packages.
You can test for the presence of both ``libssl.so`` and ``tls1.h`` on your
system to see if the complete OpenSSL is present

Most systems include the complete OpenSSL by default.  This is the case on
FreeBSD, and Mac OS X.  Debian users should install ``openssl`` and
``libssl-dev``.  SUSE users will need to install the package
``libopenssl-devel``.


TLS/SSL Certificate
-------------------

The EDRN public portal allows certain users to log in with a username and
password and gain access to private information.  To protect this information,
as well as usernames and passwords, the portal allows for HTTP over TLS/SSL,
or in other words, the HTTPS protocol.

Ensure that there is no password protecting the key file; otherwise a human
being must be present to start the web server to provide it.  The public key
should be named ``server.crt`` and placed in the extracted portal's ``etc``
directory.  The private key should be named ``server.key`` and placed in
the same directory.


Internet Connection
-------------------

The EDRN public portal is deployed using Buildout_.  Buildout automates the
retrieval and compilation of the components that comprise the portal,
configuration of those components, as well as population of the portal's
content.  Therefore, you'll need an active internet connection to deploy the
portal.


Installation
============

To install the EDRN public portal, first ensure the target system meets the
requirements in the above section.  Then, follow the steps described in this
section, below.  Installation is largely automatic and requires only a few
commands.

In summary, the installation steps are:

1.  Extract the archive.
2.  Configure it.
3.  Bootstrap it.
4.  Deploy it.
5.  Populate it.
6.  Link its logrotate files.
7.  Make it run at boot-up.

You'll need root privileges for several of these steps.


Extracting the Archive
----------------------

To extract the archive:

1.  Pick a directory where the portal and all of its supporting files will
    live, such as /usr/local, /opt, /var, etc.  You could create a specific user
    for the EDRN public portal, say ``edrn`` and use /home/edrn, /Users/edrn, etc.
    Change the current working directory to the target directory.
2.  Decompress and extract the archive.  Depending on your operating system,
    and of the following commands should work::
    
        tar xjf edrn.nci.nih.gov.tar.bz2
        gtar xjf edrn.nci.nih.gov.tar.bz2
        bzip2 -c edrn.nci.nih.gov | tar xf -
        
3.  Change the current working directory to the newly extracted
    ``edrn.nci.nih.gov`` directory.


Configuring the Portal and SSL Certificates
-------------------------------------------

To configure the portal, edit the ``operations.cfg`` file and make the
following adjustments as needed:

1.  In the [instance-settings] section, set a username and password for the
    Zope application server.
2.  In the [supervisor-settings] section, set a username and password for the
    Supervisor process monitor.
3.  If the final web address of the EDRN public portal is *not* going to be
    http://edrn.nci.nih.gov/, adjust the hostname in the [hosts] section.
4.  In the [users] section, set the effective user ID to use when running the
    components.  Common settings are ``www``, ``wwwrun``, ``httpd``, etc.  If
    you created a custom user for the portal, such as ``edrn``, you'll want to
    use that user ID.

    *Important*: ensure a group of the same name as the user you select also
    exists!

5.  Adjust the ``cpu`` and ``target`` settings in the [build] section.

Also, copy the SSL certificate files to the extracted ``etc`` directory.  The
public key should be in PEM format and named ``server.crt``.  The private key
should also be in PEM format and named ``server.key``.  For convenience,
remove any passphrase from the private key.


Bootstrapping the Buildout
--------------------------

The portal uses the Buildout_ system to construct, configure, and deploy
itself.  You don't need to download Buildout, though.  A bootstrapping file is
included that takes care of that.

To bootstrap, run::

    python2.4 bootstrap.py -dc operations.cfg
    

Deploying the Portal
--------------------

To deploy the portal, do the following:

1.  Buildout the operational environment by running::

        bin/buildout -c operations.cfg
    
    During the buildout, you may see messages similar to any of the following:

    * Couldn't develop '/some/path/edrn.nci.nih.gov/...' (not found)
    * Download error: unknown url type: https -- Some packages may not be found!
    * Download error: (110, 'Connection timed out') -- Some packages may not be found!
    * SyntaxError: 'return' outside function
    * Error: only root can use -u USER to change users

    These may all be ignored.  This step takes quite a bit of time; if you're
    fond of coffee, you may wish to use this opportunity to procure a cup.

2.  Execute the tests by running::

        python2.4 support/runtests.py
        
    All of the tests should pass.  The tests will write log files into the
    ``var/testlogs`` directory, if you're curious or wish to investigate any
    failures.  Executing the tests also takes a long time.  You may wish to
    find out what games are installed on your computer and explore a few.

3.  Populate the EDRN Public Portal with its initial content by running::

        bin/buildout -c operations.cfg install edrnsite

    This step also takes quite a bit of time; if it's close to lunch time, you
    may wish to go out to eat at this juncture.

4.  Change ownership of the ``parts`` and ``var`` directory to the effective
    user ID you set in the ``operations.cfg`` file.  For example::

        sudo chown -R wwwrun parts var

5.  Start the Supervisor as root::

        sudo bin/supervisord
        
You can then visit the Supervisor's web interface with a browser.  Unless you
changed the port setting in ``operations.cfg``, the Supervisor listens on port
9001, ie, http://localhost:9001/.  From the web interface you can check on the
status of the processes that run the portal, view their log files, stop and
restart them, etc.  If you don't like web browsers, you can also access the
Supervisor by running ``bin/supervistorctl``.

All of the following processes should be listed as running:

============== =========================================================
Process ID     Description
============== =========================================================
``balancer``   HAProxy load balancer to the two Zope application servers
``cache``      Varnish reverse proxy caching engine
``instance1``  First Zope application server
``instance2``  Second Zope application server
``main``       Nginx front-end web server
``zeo``        Zope Enterprise Objects database server
============== =========================================================

The portal itself should be available on both ports 80 and 443 on its main
hostname (unless overridden in ``operations.cfg``), ie,
http://edrn.nci.nih.gov/ and https://edrn.nci.nih.gov/.

If you need to re-do any of the installation steps, you can shutdown the
Supervisor and all of its processes by running::

    bin/supervisorctl shutdown
    
The ``supervisorctl`` command provides additional commands; run it with
``help`` as an argument for more, or give it no arguments to enter an
interactive command-line mode.


Post-Deployment Configuration
-----------------------------

The EDRN public portal requires little configuration after deployment.  The
only thing you may need to adjust is how it contacts the SMTP server in order
for it to send out password reminders, newsletters, and so forth.

By default, it will use the SMTP server on localhost without a username or
password.  If you need to change that, do the following:

1.  Visit the portal's ``plone_control_panel`` with a browser at the address
    http://edrn.nci.nih.gov/plone_control_panel

2.  Log in using the Zope application server username and password you set in
    the operations.cfg file.

3.  Click on "Mail".

4.  Adjust the SMTP settings on the form and click "Save".


Pruning Log Files
-----------------

During the operational buildout, a configuration file compatible with
logrotate_ was generated and placed in ``operations/logrotate.conf``.  If your
system uses logrotate to prune log files periodically, you can either link or
copy that generated file to ``/etc/logrotate.d``; for example::

    sudo ln -s /home/edrn/edrn.nci.nih.gov/operations/logrotate.conf /etc/logrotate.d/edrn-portal

If you don't have logrotate, you'll want to arrange for the following log
files to be rotated and the listed signal sent to the given process to have it
close its log file and start a new one:

+------------------------+--------+-------------------+
| Log File               | Signal | Process ID file   |
+========================+========+===================+
| var/log/instance1*.log | USR2   | var/instance1.pid |
+------------------------+--------+-------------------+
| var/log/instance2*.log | USR2   | var/instance2.pid |
+------------------------+--------+-------------------+
| var/log/zeoserver.log  | USR2   | var/zeoserver.pid |
+------------------------+--------+-------------------+
| var/log/main*.log      | USR1   | var/main.pid      |
+------------------------+--------+-------------------+


Starting the Portal after Reboot
--------------------------------

To ensure the EDRN public portal is always available, you should arrange to
have it started at boot-up time.  How you do so depends on your operating
system.  You may need to:

* Create a SysV-style init script in /etc/init.d that calls
  ``bin/supervisord`` to start and ``bin/supervisorctl shutdown`` to stop
* Add execution of ``bin/supervisord`` to /etc/rc.local
* Add ``bin/supervisord`` to the ``@reboot`` event of root's crontab
* Something even more exotic

Consult your operating system documentation for details.


Questions, Bug Reports, and Help
================================

For feedback about this product, please visit the feedback page at
http://cancer.jpl.nasa.gov/contact-info.


Development
===========

If you're a developer of the EDRN public portal, take a look at
DEV-README.txt.


.. References:
.. _APT: http://www.debian.org/doc/manuals/apt-howto/
.. _Buildout: http://www.buildout.org/
.. _Debian: http://www.debian.org/
.. _EDRN: http://edrn.nci.nih.gov/
.. _FreeBSD: http://www.freebsd.org/
.. _GCC: http://gcc.gnu.org/
.. _GNU Make: http://www.gnu.org/software/make/
.. _HAProxy: http://haproxy.1wt.eu/
.. _logrotate: http://linuxcommand.org/man_pages/logrotate8.html
.. _Mac OS X: http://www.apple.com/macosx/
.. _Nginx: http://wiki.nginx.org/Main
.. _OpenSSL: http://www.openssl.org/
.. _PIL: http://pythonware.com/products/pil/
.. _Plone: http://plone.org/
.. _Postfix: http://www.postfix.org/
.. _Python source: http://python.org/download/releases/2.4.6/
.. _Python: http://python.org/
.. _Supervisor: http://supervisord.org/
.. _SUSE: http://www.novell.com/linux/
.. _Varnish: http://varnish-cache.org/
.. _Xcode: http://developer.apple.com/TOOLS/Xcode/
.. _Zope: http://zope.org/


.. Author:
    Sean Kelly
    Jet Propulsion Laboratory
    California Institute of Technology

.. Copyright:
    Copyright 2010 California Institute of Technology. ALL RIGHTS RESERVED.
    U.S. Government sponsorship acknowledged.
