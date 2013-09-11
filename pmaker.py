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
import re

parser = argparse.ArgumentParser()
parser.add_argument(
	"name", help="The project name")
parser.add_argument(
	"language", help="The project language (c, cpp)")
parser.add_argument(
	"--git", help="Enable Git repository creation", action="store_true")
parser.add_argument(
	"--raze", help="Remove all contents of the project directory first", action="store_true")
parser.add_argument(
	"--cpp11", help="Enable C++11 (C++0X) in CMakeLists.txt", action="store_true")
parser.add_argument(
	"--c99", help="Enable C99 in CMakeLists.txt", action="store_true")
parser.add_argument(
	"--c11", help="Enable C11 in CMakeLists.txt", action="store_true")
parser.add_argument(
	"--libs", help="Libraries to use")

args = parser.parse_args()

libs = {
	"cpp/c" : ["opengl","glsdk"],
	"cpp" : ["boost","sfml","librocket"]
}

PNAME = args.name + "/"
p_prefix = ""
inside = False
if os.getcwd().split(os.sep)[-1] == "pmaker":
	p_prefix = "../"
	inside = True
	print("We are inside the pmaker directory!")
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
			print("Creating path '%s'" % paths[i])
			os.makedirs(paths[i])

def raze(do):
	if do:
		if str(raw_input("Do you really want to raze (y/N)? ")).lower() == "y":
			if os.path.isdir(path(PNAME)) and do:
				print("Razing...")
				for r, ds, fs in os.walk(path(PNAME)):
					for f in fs:
						os.unlink(os.path.join(r, f))
					for d in ds:
						shutil.rmtree(os.path.join(r, d))
		else:
			print("Not razing after all...")

def prepareres(res):
	pre = "files/"
	if not inside:
		pre = "pmaker/" + pre
	return pre + res

def prepareobj(res, sub = ''):
	return path(PSOURCE + sub + '/' + res)

def docopies(files):
	for r in files:
		print("Copying '{0}' to '{1}'".format(r["from"],r["to"]))
		shutil.copy(r["from"],r["to"])

def copyfiles():
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
	
	already = False
	
	for r in final:
		if os.path.isfile(r["to"]):
			already = True
	
	if already:
		if str(raw_input("Replace existing files (y/N)? ")).lower() == "y":
			docopies(final)
	else:
		docopies(final)

def putlibs(filec, out, lang):
	for lib in libs[lang]:
		if any(ulib == lib for ulib in args.libs.split(',')):
			print("Specifying '{0}' ({1}) library in CMakeLists.txt...".format(lib, lang))
			filec = filec.replace("#USE{0}#".format(lib.upper()), open(prepareres("modules/{0}.txt".format(lib))).read())
	
	f = open(prepareobj("CMakeLists.txt"),'w')
	f.write(filec)
	f.close()
	return filec
		
def cmakeset():
	s = open(prepareobj("CMakeLists.txt")).read()
	s = s.replace('__projxxxname__', args.name)
	print("Setting compilation flags...")
	if args.language == "cpp":
		if args.cpp11:
			s = s.replace('#USECPP11#', 'SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")')
			print("Using C++11 (C++0x) compile otion...")
	elif args.language == "c":
		if args.c99:
			s = s.replace('#USEC99#', 'SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c99")')
			print("Using C99 compile otion...")
		elif args.c11:
			s = s.replace('#USEC99#', 'SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c11")')
			print("Using C111 compile otion...")
	
	if args.libs != None:
		for lang in libs:
			if lang == args.language or any(subl == args.language for subl in lang.split('/')):
				s = putlibs(s, open(prepareobj("CMakeLists.txt"),'w'), lang)
	else:
		print("Not using external libraries.")

def checkgit():
	if os.path.isdir(PSOURCE + "/.git"):
		if str(raw_input("A Git repo already exists. Re-initialize (y/N)? ")).lower() == "y":
			return True
		else:
			return False
	else:
		return True

def startgit(do):
	if do:
		if checkgit():
			print "Initializing local Git repository..."
			execute("git init {0}".format(PSOURCE))

if(__name__ == "__main__"):
	raze(args.raze)
	createdirs()
	copyfiles()
	cmakeset()
	startgit(args.git)
	print "We're done! Enjoy your new project!"
