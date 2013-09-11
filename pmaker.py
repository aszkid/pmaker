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
import pprint
import fileinput

parser = argparse.ArgumentParser()
parser.add_argument(
	"name", help="The project name")
parser.add_argument(
	"language", help="The project language (c, cpp)")
parser.add_argument(
	"--git", help="Disable Git repository creation", action="store_true")
#parser.add_argument(
#	"--defs", help="Disable default files creation", action="store_true")
parser.add_argument(
	"--raze", help="Remove all contents of the project directory first", action="store_true")
parser.add_argument(
	"--cpp11", help="Enable C++11 (C++0X) in CMakeLists.txt", action="store_true")
parser.add_argument(
	"--c99", help="Enable C99 in CMakeLists.txt", action="store_true")
parser.add_argument(
	"--c11", help="Enable C11 in CMakeLists.txt", action="store_true")

args = parser.parse_args()

PNAME = args.name + "/"
p_prefix = ""
inside = False
if os.getcwd().split(os.sep)[-1] == "pmaker":
	p_prefix = "../"
	inside = True
	print "We are inside the pmaker directory!"
PSOURCE = PNAME + "source"

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

def prepareres(res):
	pre = "files/"
	if not inside:
		pre = "pmaker/" + pre
	return pre + res
def prepareobj(res, sub = ''):
	return path(PSOURCE + sub + '/' + res)

def copyfiles(defs):
	general = [".gitignore", "CMakeLists.txt"]
	specific = {
		"cpp" : {
			"src": ["main.cpp"]
		},
		"c" : {
			"src" : ["main.c"]
		}
	}
	final = []
	for f in general:
		final.append(dict([('from', prepareres(f)), ('to', prepareobj(f))]))
	for lang in specific:
		if args.language == lang:
			for t in specific[lang]:
				for f in specific[lang][t]:
					final.append(dict([('from',prepareres(f)),('to',prepareobj(f,"/"+t))]))
	
	for r in final:
		print "Copying '{0}' to '{1}'".format(r["from"],r["to"])
		shutil.copy(r["from"],r["to"])

def cmakeset():
	for line in fileinput.input(prepareobj("CMakeLists.txt"),inplace=1):
		print line.replace("__projxxxname__", args.name)
		if args.language == "cpp":
			if args.cpp11:
				print line.replace("")
			

if(__name__ == "__main__"):
	raze(args.raze)
	createdirs()
	copyfiles(True) #args.defs
	cmakeset()
