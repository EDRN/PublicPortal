*****************************
 Post NCI Installation Notes
*****************************

There are a few things that we haven't yet completed automated when it comes to
deploying the EDRN Public Portal at the National Cancer Institute.  This
document outlines the additional necessary steps.  Note that this applies only
to the staging (``edrn-test.nci.nih.gov``) and development
(``edrn-dev.nci.nih.gov``) environments.  These instructions do *not* apply to
the production (``edrn.nci.nih.gov``) environment.


RAM Cache
=========

Due to a deficiency in ``plone.app.ldap``, the ``acl_users`` isn't associated
with the ``RAMCache``, leading every single HTTP request (including icons, style
sheets, JavaScript resources, etc.) to re-authenticate with LDAP.  This makes
the experience miserable and slow.  So the first thing you need to do after a
new EDRN Portal is deployed is:

1.  Visit ``PORTAL_URL/login_form`` and log in with your EDRN username and
    password.  It'll be slow.  You must use a "superuser" username.
2.  Visit ``PORTAL_URL/manage_main/RAMCache``.  It'll be slow.
3.  Click the "Associate" tab.  It'll be slow.
4.  Click the "Locate" button.  It'll be slow.
5.  Check the box by ``acl_users`` and click "Save Changes".  It's now fast.


Login Scripts
=============

For EDRN portals in staging (``edrn-test.nci.nih.gov``) and development
((``edrn-dev.nci.nih.gov``)), we need to bring in local customizations to
Plone's various login scripts in order to work around vulnerabilities detected
by CBIIT's AppScan.  The scripts that need to be migrated are:

• ``failsafe_login_form``
• ``logged_in``
• ``login_form``
• ``login_form_validate``
• ``login_next``
• ``login_password``

To do so, do the following for each SCRIPT above:

1.  Visit https://edrn.nci.nih.gov/portal_skins/custom in a browser; click the
    name of the SCRIPT in the list.  This is the *source*.
2.  Go ``PORTAL_URL/portal_skins/plone_login/SCRIPT/manage_main``
    in another window, then click "Customize".  This is the *target*.
3.  Select all the text in the *source* and copy it to the paste board.
4.  Select all the text in the *target* and paste, overwriting the text.
5.  Click "Save Changes".

Repeat this for each of the scripts.  Remember this needs to be done only in
the staging and development environments.  The production environment of
course already has these local customizations because that's where we're
copying them from.


Create local AppScan User
=========================

We need to create a special "appscan" user that the AppScan can use to log into
the system.  To do so:

1.  Visit ``PORTAL_URL/acl_users/source_users/manage_users``.
2.  Click (Add a User).
3.  Enter user ID ``appscan``, login name ``appscan`` and a password twice.
    Then click "Add User".
4.  Store the username and password on the host ``nciws-d624-v.nci.nih.gov``
    in the file ``/web/edrn/appscan.txt``.
5.  Test that you can log into ``PORTAL_URL/login_form`` using the ``appscan``
    username and password in a different browser.


Disable Login-Lockout
=====================

The AppScan will be testing various bad passwords to try to break into the
EDRN Portal, and the Login-Lockout system will detect this and block the
``appscan`` user.  As a result, we need to disable the Login-Lockout system.
Here's how:

1.  Visit ``PORTAL_URL`` and at the bottom click "Site Setup".
2.  Click Add-ons.
3.  Check the box by "LoginLockout" and click "Deactivate".

If only that were sufficient.  We now need to remove LoginLockout from
each of the access control plugins.  To do this:

1.  Visit ``PORTAL_URL/acl_users/plugins/manage_plugins``.
2.  Click each Plugin Type in the list.
3.  If ``login_lockout_plugin`` appears in the "Active Plugins" box,
    select it and press the ⬅︎ to deactivate it.
4.  Go back one page and repeat for the next Plugin Type.


Disable Email Transmission
==========================

The AppScan can trigger emails to be sent (think Plone's content rules that
can send an email when an item is changed).  That sucks for anyone who gets
spammed by the scan.  Previously, we've disabled Plone's content rules, but
the scan somehow turns it back on.  So, we take an extra step:

1.  Visit ``PORTAL_URL`` and at the bottom click "Site Setup".
2.  Click "Content Rules".
3.  Uncheck the "Enable globally" box and click "Save".
4.  On the left, click "Mail".
5.  For SMTP server, enter ``non.exist.ent``.
6.  For "Site 'From' adress", enter ``nobody@non.exist.ent``.
7.  Click "Save".


Conclusion
==========

That's it!  The staging (``edrn-test.nci.nih.gov``) or development
(``edrn-dev.nci.nih.gov``) EDRN portal is now ready for AppScan.

We should automate this some day.
