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
    bin/buildout -c dev.cfg                    # build it
    bin/buildout -c dev.cfg install edrnsite   # deploy it
    bin/supervisord                            # start the database
    bin/instance-debug fg                      # start the app server
    ...                                        # visit http://localhost:8080/edrn, notice a bug
    CTRL+C                                     # stop the app server
    bin/develop checkout edrnsite.policy       # say the bug's in edrnsite.policy
    bin/buildout -c dev.cfg                    # let the buildout notice the new dev egg
    vi src/edrnsite.policy/../test.py          # make a test case to expose the bug
    bin/instance-debug test -s edrnsite.policy # ensure failure
    vi src/ednrsite.policy/../menu.py          # make the fix
    bin/instance-debug test -s edrnsite.policy # ensure success
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
nutshell, that means you need gcc, make, Python 2.4, and the Python Imaging
Library.  All the other dependent components will be downloaded, configured,
and deployed automatically.


Compiling and Testing
=====================

To get your development environment ready for action, check out and bootstrap
the EDRN public portal, using a Buildout_ procedure like the following::

    svn co http://tumor.jpl.nasa.gov/repo/ic/app-server/edrn.nci.nih.gov/trunk edrn.nci.nih.gov
    cd edrn.nci.nih.gov
    python2.4 bootstrap.py -c dev.cfg
    bin/buildout -c dev.cfg
    python2.4 runtests.py

This gives you an EDRN portal with the release versions of each component and
runs their tests, which had better damn well all be successful.


Viewing Your Local Portal
=========================

Right now, you've got all the software set up and configured, but your
application server's bare.  You need to actually install the EDRN public
portal.  To do that, run::

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
