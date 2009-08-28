#!/usr/bin/env python
# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Fixes Cyrus SASL.  Version 2.1.23 of Cyrus SASL configures itself
incorrectly when configured with --enable-static.  The recommended workaround
is to execute "make" twice.  This pre-make hook executes make and ignores the
error, so that when Buildout does the cmmi recipe's make, it'll succeed.

Thanks, CMU.
'''

import subprocess

def main(options, buildout):
    make = subprocess.Popen(['make', 'all'], shell=True)
    make.wait()
    
