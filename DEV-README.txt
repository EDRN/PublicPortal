*******************************************************************
 Development of the Early Detection Research Network Public Portal
*******************************************************************

.. contents::

Welcome to the Early Detection Research Network (EDRN_) public portal and
knowledge environment.  If you're *not* a developer of the portal, there's no
need to read this document.  Instead, check out the README.txt.  It'll tell
you what you need and how to install the portal.

If you're a developer, read on.


Quick Start
===========

Are you hard core?  Forget documentation!  Try the following::

    svn co http://tumor.jpl.nasa.gov/repo/ic/app-server/edrn.nci.nih.gov/trunk edrn.nci.nih.gov
    cd edrn.nci.nih.gov
    python2.4 bootstrap.py -dc dev.cfg         # bootstrap it
    bin/buildout -c dev.cfg                    # build it in "developer mode"
    support/devrebuild.sh                      # sit back and relax
    bin/instance-debug fg                      # start the app server
    ...                                        # visit http://localhost:8080/edrn, notice a bug
    CTRL+C                                     # stop the app server
    bin/develop checkout edrnsite.policy       # say the bug's in edrnsite.policy
    bin/buildout -c dev.cfg                    # let the buildout notice the new dev egg
    vi src/edrnsite.policy/.../test.py         # make a test case to expose the bug
    bin/roadrunner -s edrnsite.policy          # ensure failure
    vi src/ednrsite.policy/.../menu.py         # make the fix
    bin/roadrunner -s edrnsite.policy          # ensure success
    bin/instance-debug fg                      # start the app server
    ...                                        # re-visit http://localhost:8080/ern
    ...                                        # bask in your bug fix glory


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
requirements listed in the "Requirements" section of README.txt.  In a
nutshell, that means you need gcc, make, and Python 2.4.  All the other
dependent components will be downloaded, configured, and deployed
automatically.


Python 2.4
----------

Getting a version of Python that supports development can be tricky,
especially on Mac OS X 10.6 "Snow Leopard".  By far the easiest way to get a
decent Python version, regardless of what platform you're on, is to use the
Plone Collective Python Buildout:

1. svn co http://svn.plone.org/svn/collective/buildout/python
2. python bootstrap.py -d
3. bin/buildout
4. sudo bin/install-links

You'll be left with /opt/local/bin/python2.4 (as well as other versions),
ready to go and pre-loaded with all needed dependencies.

Want the links in /home/python instead of /opt/local?  Don't need Python 2.5,
2.6?  Want 3.1 as well?  Easy.  Make a file, say local.cfg, with the
following::

    [buildout]
    extends =
        src/base.cfg
        src/readline.cfg
        src/libjpeg.cfg
        src/python24.cfg
        src/python31.cfg
        src/links.cfg
    parts =
        ${buildout:base-parts}
        ${buildout:readline-parts}
        ${buildout:libjpeg-parts}
        ${buildout:python24-parts}
        ${buildout:python31-parts}
        ${buildout:links-parts}
    python-buildout-root = ${buildout:directory}/src
    eggs-directory = eggs
    [install-links]
    prefix = /home/python

Then build as follows:

1. python boostrap.py -dc local.cfg
2. bin/buildout -c local.cfg
3. sudo bin/install-links

You can even set the install-links prefix to the bin directory of the buildout
itself, keeping everything in one nice package.  When doing so, run "yes n |
bin/install-links".

For the EDRN Portal, use this generated python2.4 executable link instead of
any system-provided one.


Compiling and Testing
=====================

To get your development environment ready for action, check out and bootstrap
the EDRN public portal, using a Buildout_ procedure like the following::

    svn co http://tumor.jpl.nasa.gov/repo/ic/app-server/edrn.nci.nih.gov/trunk edrn.nci.nih.gov
    cd edrn.nci.nih.gov
    python2.4 bootstrap.py -dc dev.cfg
    python2.4 runtests.py

This gives you an EDRN portal with the release versions of each component and
runs their tests, which had better damn well all be successful.  Then, it puts
your buildout into "developer's mode", which is a mode for developers.  They
like it that way.


Viewing Your Local Portal
=========================

Right now, you've got all the software set up and configured, but your
application server is bare.  You need to actually install the EDRN portal into
the application server.  To do that, you need to

1. Download a snapshot of the portal database from NCI
2. Extract the snapshot into your local database
3. Upgrade the database 


  To do that, run::

    bin/buildout -c dev.cfg install edrnsite

This can take quite a bit of time.  Once it's complete, start the database::

    bin/supervisord
    
The Supervisor daemon will start and monitor the database process for you
(fire and forget).  Next, start the application server::

    bin/instance-debug fg
    
You can stop the application server by interrupting it (usually CTRL+C).  With
the application server running, your copy of the portal will be visible at
http://localhost:8080/edrn.


Developing
==========

By default, the buildout will use the last published releases of each of the
EDRN portal's components.  Typically, you'll need not the last published
release, but the latest trunk in our Subversion repository.

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
``src`` and running ``svn update``.  But there's an easier way::

    bin/develop update
    
This has the added benefit of working with other version control systems; you
don't need to worry about Subversion.


Help
----

The ``bin/develop`` command supports other options.  Run ``bin/develop help``
for more details.


Redeploying the Portal
======================

If you've made significant software changes or have otherwise munged the state
of your copy of the EDRN portal, you can re-deploy it.  To do so, you must
first shutdown your application server, usually by interrupting it (with
CTRL+C).  You'll then need to stop the database server and Supervisor::

    bin/supervisorctl shutdown
    
You can then redeploy by running::

    bin/buildout -c dev.cfg install edrnsite
    

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
    Copyright 2009 California Institute of Technology. ALL RIGHTS RESERVED.
    U.S. Government sponsorship acknowledged.
