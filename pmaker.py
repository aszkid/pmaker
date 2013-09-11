#!/usr/bin/python
# -*- coding: utf-8 -*-
# -------------------------------
# PMAKER - Project Maker
# -> The project bootstrapper
# Author: aszkid
# -------------------------------

import argparse, subprocess, os, shutil, fileinput, re, sys

# -------------------------------
# Arguments configuration
# -------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("name", help="The project name", type=str)
parser.add_argument("language", help="The project language (c, cpp)", type=str)
parser.add_argument("--libs", help="Libraries to use", type=str)
parser.add_argument("--path", help="Specify a different project path", type=str)
parser.add_argument("--git", help="Create a local Git repository after project startup", action="store_true")
parser.add_argument("--clean", help="Remove all contents of the project directory before starting", action="store_true")
parser.add_argument("--cpp11", help="Force C++11 ('-std=c++11') in CMakeLists.txt", action="store_true")
parser.add_argument("--c99", help="Force C99 ('-std=c99') in CMakeLists.txt", action="store_true")
parser.add_argument("--c11", help="Force C11 ('-std=c11') in CMakeLists.txt", action="store_true")

# -------------------------------
# General variables
# -------------------------------
ARGS = parser.parse_args()							# Parsed arguments
PNAME = ARGS.name									# Project name
PPATH = (ARGS.path if ARGS.path != None else PNAME) + "/"	# Project path
SPATH = "pmaker/"									# Source path (the pmaker path)
RPATH = "files/"									# Resources path (inside SPATH)

# -------------------------------
# Some helper functions
# -------------------------------

# CMake variable expander
def cmake_set(var, val, rec = False):
	if not rec:
		return 'SET({0} "{1}")'.format(var, val)			# Return typical variable setting (e.g, 'SET(SOME_VAR "somevalue")')
	else:
		return 'SET({0} "${{{0}}} {1}")'.format(var, val)		# Return 'recursive' variable setting (e.g, 'SET(SOME_VAR "${SOME_VAR} somevalue")')

# Path helpers
def make_source(name, sub = None):
	return "{0}{1}{2}{3}".format(SPATH, RPATH, (sub + "/") if sub else str(), name)		# Return resource path (e.g, pmaker/files/modules/boost.txt)
def make_dest(name, sub = None):
	return "{0}{1}{2}".format(PPATH, (sub + "/") if sub else str(), name)				# Return destination path (e.g, yourprojname/source/inc/lelp.hpp)

# User confirmation input, based on msg and preferred var (yes or no). Nice shortcut
def user_confirm(msg, pref="y"):
	r = str(raw_input(msg + " (" + ("Y/n" if pref == "y" else "y/N") + ")? ")).lower()
	if r == "y":
		return True
	elif r == "n":
		return False
	else:
		return True if pref == "y" else False

# Check if a variable matches any element of a list
def matches_any(var, source):
	return any(sub == var for sub in source)
	
# Check if a path exists
def path_exists(p):
	return os.path.isdir(p)

# -------------------------------
# DA CONFIG DICTIONARY
# -------------------------------

CFG = {
	"langs" : {
		"cpp/c" : {
			"pure" : False,
			"libs" : ["opengl","glsdk"],
			"flags" : [],
			"paths" : [					#Relative to 'projname/'
				"source",
				"projects",
				"source/inc",
				"source/src"
			]
		},
		"cpp" : {
			"pure" : True,
			"libs" : ["boost", "sfml"],
			"flags" : [
				{
					"name"		: "stdcpp11",
					"excludes"	: "",
					"from"		: "#STDCPP11#",
					"to"			: cmake_set("CMAKE_CXX_FLAGS", "-std=c++11", True),
					"desc"		: "Using C++11 compile flag..."
				}
			],
			"paths" : []
		},
		"c" : {
			"pure" : True,
			"libs" : [],
			"flags" : [
				{
					"name"		: "stdc99",
					"excludes"	: "stdc11",
					"from"		: "#STDC99#",
					"to"			: cmake_set("CMAKE_C_FLAGS", "-std=c99", True),
					"desc"		: "Using C99 compile flag..."
				},
				{
					"name"		: "stdc11",
					"excludes"	: "stdc99",
					"from"		: "#STDC11#",
					"to"			: cmake_set("CMAKE_C_FLAGS", "-std=c11", True),
					"desc"		: "Using C11 compile flag..."
				}
			],
			"paths" : []
		}
	}
}

# -------------------------------
# BASE APPLICATION FUNCTIONS
# -------------------------------

# STEP NO. 0 - Check if language is existent
def check_lang():	
	for subl in CFG.get("langs"):
		if (CFG.get("langs").get(subl).get("pure") == True) and (ARGS.language == subl):
			print "Language selected ({0}) is correct...".format(ARGS.language)
			return True
	print "Language selected ({0}) is not in pmaker's database! Exiting.".format(ARGS.language)
	return False

# STEP NO. 1 (Optional) - Clean project directory
def clean_proj():
	if (ARGS.clean == True) and (user_confirm("Really clean project path","n")):
		print "Cleaning project path ({0})...".format(PPATH)
		for r, ds, fs in os.walk(PPATH):
			for f in fs:
				os.unlink(os.path.join(r, f))
			for d in ds:
				shutil.rmtree(os.path.join(r, d))
	else:
		print "Not cleaning project path..."

# STEP NO. 2 - Create necessary folders
def make_paths():
	path_queue = []

	if not path_exists(PPATH):
		print "Creating base project path '{0}'...".format(PPATH)
		path_queue.append(PPATH)
	for lang in CFG.get("langs"):
		if matches_any(ARGS.language, lang.split("/")):
			print "Creating paths for project of language '{0}'...".format(lang)
			for path in CFG.get("langs").get(lang).get("paths"):
				finalpath = PPATH + path
				if not path_exists(finalpath):
					print "Making path '{0}'...".format(finalpath)
					path_queue.append(finalpath)
	
	for p in path_queue:
		os.makedirs(p)

# STEP NO. 3 - Copy base files according to language specifications
def copy_files():
	pass

# STEP NO. 4 (CPP/C Only) - Configure CMakeLists.txt
def cmake_cfg():
	pass

# STEP NO. 5 (Optional) - Start a local Git repository
def start_git():
	pass



"""
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
"""
if(__name__ == "__main__"):
	if not check_lang():	# Step 0
		sys.exit(1)
	clean_proj()	# Step 1
	make_paths()	# Step 2
	copy_files()	# Step 3
	cmake_cfg()	# Step 4
	start_git()	# Step 5
