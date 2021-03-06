#!/usr/bin/env python

__author__    = 'Andre Merzky'
__email__     = 'andre@merzky.net'
__copyright__ = 'Copyright 2017, Hanffaser Uckermark'
__license__   = 'GPL'


""" Setup script, only usable via pip. """

import re
import os
import sys
import shutil
import subprocess as sp

name     = 'hf.sim'
mod_root = 'src/hf/sim/'

try:
    from setuptools import setup, Command, find_packages
except ImportError as e:
    print("%s needs setuptools to install" % name)
    sys.exit(1)

# ------------------------------------------------------------------------------
#
# versioning mechanism:
#
#   - version:          1.2.3            - is used for installation
#   - version_detail:  v1.2.3-9-g0684b06 - is used for debugging
#   - version is read from VERSION file in src_root, which then is copied to
#     module dir, and is getting installed from there.
#   - version_detail is derived from the git tag, and only available when
#     installed from git.  That is stored in mod_root/VERSION in the install
#     tree.
#   - The VERSION file is used to provide the runtime version information.
#
def get_version (mod_root):
    """
    mod_root
        a VERSION file containes the version strings is created in mod_root,
        during installation.  That file is used at runtime to get the version
        information.  
        """

    try:

        version_base   = None
        version_detail = None

        # get version from './VERSION'
        src_root = os.path.dirname (__file__)
        if  not src_root:
            src_root = '.'

        with open (src_root + '/VERSION', 'r') as f:
            version_base = f.readline ().strip()

        # attempt to get version detail information from git
        # We only do that though if we are in a repo root dir, 
        # ie. if 'git rev-parse --show-prefix' returns an empty string --
        # otherwise we get confused if the ve lives beneath another repository,
        # and the pip version used uses an install tmp dir in the ve space
        # instead of /tmp (which seems to happen with some pip/setuptools 
        # versions).
        p = sp.Popen ('cd %s ; '\
                      'test -z `git rev-parse --show-prefix` || exit -1; '\
                      'tag=`git describe --tags --always` 2>/dev/null ; '\
                      'branch=`git branch | grep -e "^*" | cut -f 2- -d " "` 2>/dev/null ; '\
                      'echo $tag@$branch'  % src_root,
                      stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        version_detail = str(p.communicate()[0].strip())
        version_detail = version_detail.replace('detached from ', 'detached-')

        # remove all non-alphanumeric (and then some) chars
        version_detail = re.sub('[/ ]+', '-', version_detail)
        version_detail = re.sub('[^a-zA-Z0-9_+@.-]+', '', version_detail)

        if  p.returncode   !=  0  or \
            version_detail == '@' or \
            'not-a-git-repo' in version_detail or \
            'not-found'      in version_detail or \
            'fatal'          in version_detail :
            version = version_base
        elif '@' not in version_base:
            version = '%s-%s' % (version_base, version_detail)
        else:
            version = version_base

        # make sure the version files exist for the runtime version inspection
        path = '%s/%s' % (src_root, mod_root)
        with open (path + "/VERSION", "w") as f:
            f.write (version + "\n")

        sdist_name = "%s-%s.tar.gz" % (name, version)
        sdist_name = sdist_name.replace ('/', '-')
        sdist_name = sdist_name.replace ('@', '-')
        sdist_name = sdist_name.replace ('#', '-')
        sdist_name = sdist_name.replace ('_', '-')

        if '--record'    in sys.argv or \
           'bdist_egg'   in sys.argv or \
           'bdist_wheel' in sys.argv    :
           # pip install stage 2 or easy_install stage 1
           #
           # pip install will untar the sdist in a tmp tree.  In that tmp
           # tree, we won't be able to derive git version tags -- so we pack the
           # formerly derived version as ./VERSION
            shutil.move ("VERSION", "VERSION.bak")           # backup version
            shutil.copy ("%s/VERSION" % path, "VERSION")     # use full version instead
            os.system   ("python setup.py sdist")            # build sdist
            shutil.copy ('dist/%s' % sdist_name,
                         '%s/%s'   % (mod_root, sdist_name)) # copy into tree
            shutil.move ("VERSION.bak", "VERSION")           # restore version

        with open (path + "/SDIST", "w") as f: 
            f.write (sdist_name + "\n")

        return version_base, version_detail, sdist_name

    except Exception as e :
        raise RuntimeError ('Could not extract/set version: %s' % e)


# ------------------------------------------------------------------------------
# check python version. we need >= 2.7, <3.x
if  sys.hexversion < 0x02070000 or sys.hexversion >= 0x03000000:
    raise RuntimeError("%s requires Python 2.x (2.7 or higher)" % name)


# ------------------------------------------------------------------------------
# get version info -- this will create VERSION and srcroot/VERSION
version, version_detail, sdist_name = get_version (mod_root)


# ------------------------------------------------------------------------------
class our_test(Command):
    user_options = []
    def initialize_options (self) : pass
    def finalize_options   (self) : pass
    def run (self) :
        testdir = "%s/tests/" % os.path.dirname(os.path.realpath(__file__))
        retval  = sp.call([sys.executable,
                          '%s/run_tests.py'               % testdir,
                          '%s/configs/basetests.cfg'      % testdir])
        raise SystemExit(retval)


# ------------------------------------------------------------------------------
#
def read(*rnames):
    try :
        return open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    except Exception :
        return ''


# ------------------------------------------------------------------------------
#
# borrowed from the MoinMoin-wiki installer
#
def makeDataFiles(prefix, dir):
    """ Create distutils data_files structure from dir

    distutil will copy all file rooted under dir into prefix, excluding
    dir itself, just like 'ditto src dst' works, and unlike 'cp -r src
    dst, which copy src into dst'.

    Typical usage:
        # install the contents of 'wiki' under sys.prefix+'share/moin'
        data_files = makeDataFiles('share/moin', 'wiki')

    For this directory structure:
        root
            file1
            file2
            dir
                file
                subdir
                    file

    makeDataFiles('prefix', 'root')  will create this distutil data_files structure:
        [('prefix', ['file1', 'file2']),
         ('prefix/dir', ['file']),
         ('prefix/dir/subdir', ['file'])]

    """
    # Strip 'dir/' from of path before joining with prefix
    dir = dir.rstrip('/')
    strip = len(dir) + 1
    found = []
    os.path.walk(dir, visit, (prefix, strip, found))
    return found

def visit((prefix, strip, found), dirname, names):
    """ Visit directory, create distutil tuple

    Add distutil tuple for each directory using this format:
        (destination, [dirname/file1, dirname/file2, ...])

    distutil will copy later file1, file2, ... info destination.
    """
    files = []
    # Iterate over a copy of names, modify names
    for name in names[:]:
        path = os.path.join(dirname, name)
        # Ignore directories -  we will visit later
        if os.path.isdir(path):
            # Remove directories we don't want to visit later
            if isbad(name):
                names.remove(name)
            continue
        elif isgood(name):
            files.append(path)
    destination = os.path.join(prefix, dirname[strip:])
    found.append((destination, files))

def isbad(name):
    """ Whether name should not be installed """
    return (name.startswith('.') or
            name.startswith('#') or
            name.endswith('.pickle') or
            name == 'CVS')

def isgood(name):
    """ Whether name should be installed """
    if not isbad(name):
        if name.endswith('.py') or name.endswith('.json'):
            return True
    return False


# -------------------------------------------------------------------------------
setup_args = {
    'name'               : name,
    'version'            : version,
    'description'        : 'Hanfbast production simulator',
    'long_description'   : (read('README.md') + '\n\n' + read('CHANGES.md')),
    'author'             : 'Andre Merzky, Hanffaser Uckermark',
    'author_email'       : 'andre@merzky.net',
    'maintainer'         : 'Andre Merzky',
    'maintainer_email'   : 'andre@merzky.net',
    'url'                : 'https://github.com/andre-merzky/hf.sim/',
    'license'            : 'GPL',
    'keywords'           : 'futuretex',
    'classifiers'        : [
        'Development Status :: 1 - Experimental',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: GPL License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],
    'namespace_packages' : ['hf'],
    'packages'           : find_packages('src'),
    'package_dir'        : {'': 'src'},
    'scripts'            : [
                            'bin/hf_sim_driver.py',
                            'bin/hf_sim_sample_props.py',
                            'bin/hf_sim_plot_hist.gplot',
                           ],
    'package_data'       : {'': ['*.txt', '*.sh', '*.json', '*.gz', 'VERSION', 'SDIST', sdist_name]},
    'install_requires'   : ['radical.utils'],
    'zip_safe'           : False,
}

# ------------------------------------------------------------------------------

setup (**setup_args)

os.system('rm -rf src/%s.egg-info' % name)

# ------------------------------------------------------------------------------

