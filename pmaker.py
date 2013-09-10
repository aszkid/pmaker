#!/usr/bin/python
# -*- coding: utf-8 -*-
# -------------------------------
# PMAKER - Project Maker
# -> The project bootstrapper
# -------------------------------

import argparse
import subprocess
import os
import shutil


parser = argparse.ArgumentParser()
parser.add_argument(
	"name", help="The project name")
parser.add_argument(
	"language", help="The project language (c, cpp)")
parser.add_argument(
	"--git", help="Disable Git repository creation", action="store_true")
parser.add_argument(
	"--defs", help="Disable default files creation", action="store_true")
parser.add_argument(
	"--raze", help="Remove all contents of the project directory first", action="store_true")

args = parser.parse_args()

PNAME = args.name + "/"
p_prefix = ""
inside = False
if os.getcwd().split(os.sep)[-1] == "pmaker":
	p_prefix = "../"
	inside = True
	print "We are inside the pmaker directory!"
PSOURCE = PNAME + "source/"

def path(p):
	return p_prefix + p

def execute(cmd):
	process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	return output.rstrip('\n')

def createdirs():
	paths = [
		PNAME, PNAME + "projs",
		PNAME + "source", PNAME + "bin",
		PNAME + "source/inc", PNAME + "source/src"
	]
	for i, p in enumerate(paths):
		paths[i] = path(paths[i])
		if not os.path.isdir(paths[i]):
			print "Creating path '%s'" % paths[i]
			os.makedirs(paths[i])

def raze(do):
	if os.path.isdir(path(PNAME)) and do:
		print "Razing..."
		execute("rm -r %s" % path(PNAME))

def copyfiles(defs):
	general = [".gitignore", "CMakeLists.txt"]
	specific = {
		"cpp" : ["main.cpp"],
		"c" : ["main.c"]
	}
	extras = {
		"cpp" : ["header.hpp", "header.cpp"],
		"c" : ["header.h", "header.c"]
	}
	for f in general:
		pre = "files/"
		if not inside:
			pre = "pmaker/files/"
		print "Copying '{0}'...".format(pre + f)
		shutil.copy(pre + f, path(PSOURCE + f))
	
		
if(__name__ == "__main__"):
	raze(args.raze)
	createdirs()
	copyfiles(args.defs)
