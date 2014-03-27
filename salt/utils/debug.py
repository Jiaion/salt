# -*- coding: utf-8 -*-
'''
Print a stacktrace when sent a SIGUSR1 for debugging
'''

# Import python libs
import os
import sys
import time
import random
import signal
import tempfile
import traceback
import inspect

# Import salt libs
import salt.utils


def _makepretty(printout, stack):
    '''
    Pretty print the stack trace and environment information
    for debugging those hard to reproduce user problems.  :)
    '''
    printout.write('======== Salt Debug Stack Trace =========\n')
    traceback.print_stack(stack, file=printout)
    printout.write('=========================================\n')


def _handle_sigusr1(sig, stack):
    '''
    Signal handler for SIGUSR1, only available on Unix-like systems
    '''
    # When running in the foreground, do the right  thing
    # and spit out the debug info straight to the console
    if sys.stderr.isatty():
        output = sys.stderr
        _makepretty(output, stack)
    else:
        filename = 'salt-debug-{0}.log'.format(int(time.time()))
        destfile = os.path.join(tempfile.gettempdir(), filename)
        with salt.utils.fopen(destfile, 'w') as output:
            _makepretty(output, stack)


def _handle_sigusr2(sig, stack):
    '''
    Signal handler for SIGUSR2, only available on Unix-like systems
    '''
    try:
        import yappi
    except ImportError:
        return
    if yappi.is_running():
        filename = 'callgrind.salt-{0}-{1}'.format(int(time.time()), os.getpid())
        destfile = os.path.join(tempfile.gettempdir(), filename)
        try :
            fd = open(destfile, "a+")
            yappi.get_func_stats().print_all(fd)
            yappi.get_thread_stats().print_all(fd)
            if sys.stderr.isatty():
                sys.stderr.write('Saved profiling data to: {0}\n'.format(destfile))
        except :
            pass
        finally :
            fd.close()
            yappi.stop()
            yappi.clear_stats()
    else:
        if sys.stderr.isatty():
            sys.stderr.write('Profiling started\n')
        yappi.start()


def _handle_sigmem(sig, stack):
    '''
    Signal handler for SIGUSR2, only available on Unix-like systems
    '''
    import gc
    try :
        import objgraph
    except ImportError:
        return 
    try :
        filename = 'mem.salt-{0}-{1}'.format(int(time.time()), os.getpid())
        destfile = os.path.join(tempfile.gettempdir(), filename)
        outs = []
        outs.append('----gc----')
        outs.append(gc.collect())
        outs.append('\n')
        outs.append('=' * 50)
        outs.append('\n')
        for t, n in objgraph.most_common_types(100):
            outs.append('{0} {1}\n'.format(t,n))
        outs.append('objgraph.by_type:\n')
        #objgraph.show_backrefs(objgraph.by_type('tuple'), filename='chain.png')
        with open(destfile, 'a+') as output:
            for x in outs:
                output.write(str(x))
    except :
        print traceback.format_exc()


def enable_sig_handler(signal_name, handler):
    '''
    Add signal handler for signal name if it exists on given platform
    '''
    if hasattr(signal, signal_name):
        signal.signal(getattr(signal, signal_name), handler)


def enable_sigusr1_handler():
    '''
    Pretty print a stack trace to the console or a debug log under /tmp
    when any of the salt daemons such as salt-master are sent a SIGUSR1
    '''
    enable_sig_handler('SIGUSR1', _handle_sigusr1)
    # Also canonical BSD-way of printing profress is SIGINFO
    # which on BSD-deriviatives can be sent via Ctrl+T
    enable_sig_handler('SIGINFO', _handle_sigusr1)


def enable_sigusr2_handler():
    '''
    Toggle YAPPI profiler
    '''
    enable_sig_handler('SIGUSR2', _handle_sigusr2)


def enable_sigmem_handler():
    '''
    mem signal handler
    '''
    enable_sig_handler('SIGRTMAX', _handle_sigmem)

def inspect_stack():
    '''
    Return a string of which function we are currently in.
    '''
    return {'co_name': inspect.stack()[1][3]}
