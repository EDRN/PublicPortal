*******************************************************************
 Development of the Early Detection Research Network Public Portal
*******************************************************************

.. contents::

Welcome to the Early Detection Research Network (EDRN_) public portal and
knowledge environment.  If you're *not* a developer of the portal, there's no
need to read this document.  Instead, check out the README.rst and
INSTALL.rst.  It'll tell you what you need and how to install the portal.

If you're a developer, read on.


Quick Start
===========

Are you hard core?  Forget documentation!  Try the following::

    git clone https://github.com/EDRN/PublicPortal.git
    cd PublicPortal
    python2.7 bootstrap.py -v 2.2.5 --setuptools-version 7.0 -c dev.cfg
    bin/buildout -c dev.cfg
    support/devrebuild.sh
    bin/instance-debug fg
    (visit http://localhost:8080/edrn/login_form)
    CTRL+C

Not working?  Read on.


Getting Started
===============

The development setup for the EDRN public portal uses a stripped-down version
of the operational setup:

* Supervisor_ process monitor, which controls ...
* ZEO database server, which answers requests from ...
* A single Zope_ application server instance, enhanced with debugging tools,
  which runs the portal and services requests from http://localhost:8080/edrn.

Setting up the above is easy.  First off, your system will need to meet the
requirements listed in the "Requirements" section of README.rst.  In a nutshell,
that means you need gcc, make, and Python 2.7.  You'll also need about 3 GiB of
free space.


Python 2.7
----------

Getting a version of Python that supports development can be tricky, especially
on Mac OS X.  By far the easiest way to get a decent Python version, regardless
of what platform you're on, is to use the Plone Collective Python Buildout:

1. git clone https://github.com/collective/buildout.python.git
2. cd buildout.python
3. Edit buildout.cfg and delete all lines for python24, 25, 32, 33, and 34.
   Leave ``src/python27.cfg`` and ``${buildout:python27-parts}`` intact.
4. /usr/bin/python bootstrap.py
5. bin/buildout
6. sudo bin/install-links

You'll be left with /opt/local/bin/python2.7 ready to go and pre-loaded with
needed dependencies.  *Use this Python executable from now on*.


Building Out
============

To get your development environment ready for action, check out and bootstrap
the EDRN public portal, using a Buildout_ procedure like the following::

    git clone https://github.com/EDRN/PublicPortal.git
    cd PublicPortal
    python2.7 bootstrap.py -v 2.2.5 --setuptools-version 7.0 -c dev.cfg
    bin/buildout -c dev.cfg

Note: this can take over 15 minutes the first time it's run.  You may also see a
lot of warnings and plenty of SyntaxErrors.  You can ignore them all.


Populating Your Portal
======================

At this point you have the portal software all set up and ready to go, but no
portal content.  To get the full operational content, run::

    support/devrebuild.sh

NOTE: This command requires access to tumor.jpl.nasa.gov.  If you're outside JPL
you'll need to start your JPL VPN.

The ``support/devrebuild.sh`` script does the following:

1. Download a snapshot of the portal database from NCI (this can take a very
   long time the first time)
2. Extract the snapshot into your local database
3. Upgrade the database    
4. Start the Supervisor daemon running the ZEO database server

Next, start the application server::

    bin/instance-debug fg
    
You can stop the application server by interrupting it (usually CTRL+C).  With
the application server running, your copy of the portal will be visible at
http://localhost:8080/edrn.


Developing
==========

By default, the buildout will use the last published releases of each of the
EDRN portal's components.  Typically, you'll need not the last published
release, but the latest master from our Git repository.

To check out a component, run::

    bin/develop checkout <component-name>
    
The ``develop`` command will check out the code from the repository and place
it in the ``src`` directory as a development egg.  You then need to inform the
buildout of the new development egg by running::

    bin/buildout -c dev.cfg
    
The buildout will notice the new egg and configure appropriately.


Updating
--------

You can update your checked out eggs by visiting each checkout directory under
``src`` and running ``git pull``.  But there's an easier way::

    bin/develop update
    
This has the added benefit of working with other version control systems; you
don't need to worry about Subversion, Git, etc.


Help
----

The ``bin/develop`` command supports other options.  Run ``bin/develop help``
for more details.


Questions, Bug Reports, and Help
================================

For feedback about this product, please visit the feedback page at
http://cancer.jpl.nasa.gov/contact-info.


.. References:
.. _Buildout: http://www.buildout.org/
.. _EDRN: http://edrn.nci.nih.gov/
.. _Supervisor: http://supervisord.org/
.. _Zope: http://zope.org/


.. Author:
    Sean Kelly
    Jet Propulsion Laboratory
    California Institute of Technology

.. Copyright:
    Copyright 2009-2015 California Institute of Technology. ALL RIGHTS
    RESERVED. U.S. Government sponsorship acknowledged.
