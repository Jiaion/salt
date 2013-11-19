#!/usr/bin/python -tt
# This program is free software; you can redistribute it and.or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#
# Copyright taobao Inc. 2009
# $Id: branch.py 2056 2009-09-23 12:04:21Z luyan $
# Author: Gao Shanyuam <shanyuan.gao@alibaba-inc.com>
#
# Examples:
#
#  yum install --branch current package
#  yum install --branch test package
#  yum install --comparch test package

import yum
import yum.plugins
import rpmUtils.arch
#print rpmUtils.arch.getBaseArch()
#print rpmUtils.arch.getCanonArch()

# Decent (UK.US English only) number formatting.
import locale
import os
import os.path
import logging
log = logging.getLogger(__name__)

locale.setlocale(locale.LC_ALL, '') 

requires_api_version = '2.1'
if yum.plugins.API_VERSION < '2.3':
    from yum.plugins import TYPE_INTERFACE
    plugin_type = (TYPE_INTERFACE,)
else:
    from yum.plugins import TYPE_INTERACTIVE
    plugin_type = (TYPE_INTERACTIVE,)

def config_hook(conduit):
    parser = conduit.getOptParser()
    parser.add_option('', '--branch', '-b', '--br', action='store',
           type='string', dest='branch', default='stable',
           metavar='[stable|current|test|data-test|data-current]',
           help="specifies the branch on YUM server(default stable)")
    parser.add_option('', '--comparch', '--ca', dest='comparch', action='store_true',
           default=False, help="allow x86_64 system use i386 arch repos")

#added by jigang.djg@2012-07-19 --start
def clean_hook(conduit):
  path="/var/cache/yum"
  for root,dirs,files in os.walk(path):
    for filespath in files:
      if "taobao" in os.path.join(root,filespath):
          #print "cleaning " +  os.path.join(root,filespath)
          os.remove(os.path.join(root,filespath))
#added by jigang.djg@2012-07-19 --finish

def prereposetup_hook(conduit):
    opts, commands = conduit.getCmdLine()
    repos = conduit.getRepos()
    # Display the options from the [main] section
    basearch = rpmUtils.arch.getBaseArch()
    releasemaj, releaseminor = getRhelRelease()
    if opts.branch == 'test':
        repos.enableRepo('taobao.' + releasemaj + '.' + basearch + '.test')
        repos.enableRepo('taobao.' + releasemaj + '.' + basearch + '.current')
        repos.enableRepo('taobao.' + releasemaj + '.' + basearch + '.stable')
        repos.enableRepo('taobao.' + releasemaj + '.noarch.test')
        repos.enableRepo('taobao.' + releasemaj + '.noarch.current')
        repos.enableRepo('taobao.' + releasemaj + '.noarch.stable')
        if opts.comparch and basearch == 'x86_64':
            repos.enableRepo('taobao.' + releasemaj + '.i386.test')
            repos.enableRepo('taobao.' + releasemaj + '.i386.current')
            repos.enableRepo('taobao.' + releasemaj + '.i386.stable')
    elif opts.branch == 'current':
        repos.enableRepo('taobao.' + releasemaj + '.' + basearch + '.current')
        repos.enableRepo('taobao.' + releasemaj + '.' + basearch + '.stable')
        repos.enableRepo('taobao.' + releasemaj + '.noarch.current')
        repos.enableRepo('taobao.' + releasemaj + '.noarch.stable')
        if opts.comparch and basearch == 'x86_64':
            repos.enableRepo('taobao.' + releasemaj + '.i386.current')
            repos.enableRepo('taobao.' + releasemaj + '.i386.stable')
    elif opts.branch == 'stable':
        repos.enableRepo('taobao.' + releasemaj + '.' + basearch + '.stable')
        repos.enableRepo('taobao.' + releasemaj + '.noarch.stable')
        if opts.comparch and basearch == 'x86_64':
            repos.enableRepo('taobao.' + releasemaj + '.i386.stable')
    elif opts.branch == 'data-test':
        repos.enableRepo('datadaily.data-test')
    elif opts.branch == 'data-current':
        repos.enableRepo('datadaily.data-current')

    else:
        print "WARNING: Unknown branch " + opts.branch + ", ignore it."
        repos.enableRepo('taobao.' + releasemaj + '.' + basearch + '.stable')
        repos.enableRepo('taobao.' + releasemaj + '.noarch.stable')
        if opts.comparch and basearch == 'x86_64':
            repos.enableRepo('taobao.' + releasemaj + '.i386.stable')
    # Display the options from the repository sections

def getRhelRelease():
    """
    get RHEL Release version from /etc/redhat-release
    """
    rf = open('/etc/redhat-release', 'r')
    if rf:
        r = rf.readline().split(' ')
        if r[6] == '4':
            maj = '4'
            minor = r[9][0]
            return maj, minor
        elif r[6][0] == '5':
            return r[6].split('.')
        elif r[6][0] == '6':
            return r[6].split('.')
        else:
            return False


