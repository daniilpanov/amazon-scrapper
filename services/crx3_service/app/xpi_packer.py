#! /usr/bin/env python
########## START INTERNAL WORK ##########
# You should not need to edit anything past this point.
# If you find that you really do, you should push your
# changes back to us so that the script can be improved.

import os
import sys
import re

import zipfile  # For working with zip archives

### Settings ###

# Files to include in the archive are selected by using include and ignore.
# include and ignore are a list of regular expressions. Files will be packed
# if they match any regular expression in include and do not match any
# expression in ignore.  All matching is done using Python re
# (http://docs.python.org/py3k/library/re.html) using the search method so you
# must explicitly write ^ if beginning of line matching is desired.  The full
# relative path is matched (beginning with a /).  Directories are not listed
# and are created as needed.  This means you can not have empty directories.
include = [".*"]
exclude = ["\.xpi$", "\~$", "\.bak$", "\/\.", "\.sh$", "\.py$", "STYLE"]

# The way to name the package.  This will be parsed using Python's Format
# String. (http://docs.python.org/py3k/library/string.html#formatstrings)  The
# package will be created in the current directory, overwriteing any file with
# the same name.
#
# Defined variables are:
# 	• {name} - the long name of the package.  This is taken from the
#		<em:name> element in install.rdf
# 	• {code} - the code or short name of the package.  This is the name used
#		in chrome urls.  This is taken from the <em:code> element in
#		install.rdf.  NOTE: this is not a standard element and will need to
#		added to install.rdf to be used.
# 	• {ver} - the version of the package.  This is taken from the <em:name>
#		element in install.rdf
xpiname = '{code}-{ver}'  # The name of the .xpi package (".xpi" is appended)

### The Info To Use ###
needname = re.compile('^(.*[^\{]|)(\{\{)*\{name\}(\}\})*([^\}].*|)$')  # If we need a name
getname = re.compile('<em:name>([^<]*)</em:name>')  # Get application name from install.rdf
needcode = re.compile('^(.*[^\{]|)(\{\{)*\{code\}(\}\})*([^\}].*|)$')  # If we need a code
getcode = re.compile('<em:code>([^<]*)</em:code>')  # Get short name from install.rdf
needver = re.compile('^(.*[^\{]|)(\{\{)*\{ver\}(\}\})*([^\}].*|)$')  # If we need a version
getver = re.compile('<em:version>([^<]*)</em:version>')  # Get application version from install.rdf


def pack(extdir, name='', ver='', code=''):
    try:
        insrdff = open(extdir + "/install.rdf")
    except:
        sys.exit("No install.rdf")
    insrdf = insrdff.read()
    if not insrdf:
        sys.exit("Bad install.rdf")
    insrdff.close()
    del insrdff

    if needname.match(xpiname):
        try:
            name = getname.search(insrdf).group(1)
        except:
            sys.exit("Could not get info: name")
    if needcode.match(xpiname):
        try:
            code = getcode.search(insrdf).group(1)
        except:
            sys.exit("Could not get info: code")
    if needver.match(xpiname):
        try:
            ver = getver.search(insrdf).group(1)
        except:
            sys.exit("Could not get info: version")

    res_xpiname = xpiname.format(name=name, code=code, ver=ver) + ".xpi"  # Handle all the variables

    ### Compile the regular expressions ###
    includere = []
    for res in include:
        includere.append(re.compile(res))

    excludere = []
    for res in exclude:
        excludere.append(re.compile(res))

    ### Create the Archive ###
    xpi = zipfile.ZipFile(res_xpiname, "w", zipfile.ZIP_STORED, True)

    ### Add Files ###
    for root, dirs, files in os.walk(extdir):
        for file in files:
            file = root + '/' + file
            filename = os.path.abspath(file)[len(extdir):]

            if os.path.isdir(file):
                filename = filename + '/'

            for rei in includere:
                if rei.search(filename):
                    for ree in excludere:
                        if ree.search(filename):
                            break
                    else:
                        isinignore = False
                        break
            else:
                isinignore = True

            if not isinignore:
                print("Adding ", filename)
                xpi.write(file, filename)

    xpi.close()  # Finalize the archive
