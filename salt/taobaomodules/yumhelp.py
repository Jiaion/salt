#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#=============================================================================
#     FileName: yumhelp.py
#         Desc: 
#       Author: linxiao.jz
#        Email: jiaion21@gmail.com
#      Version: 0.1
#   LastChange: 2013-11-19 18:32:20
#      History:
#=============================================================================


from yum.plugins import PreRepoSetupPluginConduit

class Opts():
    pass

class YumBranchHelp():
    def __init__(self, *args, **kwargs):
        self.opts = Opts()
        self.opts.branch = kwargs.get('branch')
        self.opts.comparch = kwargs.get('comparch')
        try :
            self.command = [ kwargs.get('fun')[:-2], kwargs.get('name') ]
        except :
            self.command = ['','']
        self.yumbase = kwargs.get('yumbase')
    def getCmdLine(self):
        return self.opts, self.command
    def getRepos(self):
        return self.yumbase._getRepos()


