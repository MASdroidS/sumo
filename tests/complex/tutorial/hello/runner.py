#!/usr/bin/env python
"""
@file    runner.py
@author  Daniel Krajzewicz
@date    2007-10-25
@version $Id$

This script is a test runner for the broken networks.

Copyright (C) 2008-2011 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""


import os,subprocess,sys,time
import xml.dom.minidom as dom
import shutil
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..', '..', '..', '..', "tools", "lib"))
from testUtil import checkBinary


netconvertBinary = checkBinary('netconvert')
sumoBinary = checkBinary('sumo')
# build/check network
retcode = subprocess.call([netconvertBinary, "-c", "data/hello.netc.cfg"], stdout=sys.stdout, stderr=sys.stderr)
try: shutil.copy("data/hello.net.xml", "net.net.xml")
except: print "Missing 'hello.net.xml'"
print ">> Netbuilding closed with status %s" % retcode
sys.stdout.flush()
# run simulation
retcode = subprocess.call([sumoBinary, "-c", "data/hello.sumo.cfg","--no-step-log"], stdout=sys.stdout, stderr=sys.stderr)
print ">> Simulation closed with status %s" % retcode
sys.stdout.flush()

