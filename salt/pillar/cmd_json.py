# -*- coding: utf-8 -*-
'''
Execute a command and read the output as JSON. The JSON data is then directly
overlaid onto the minion's pillar data
'''

# Import python libs
import subprocess
import logging
import json

# Set up logging
log = logging.getLogger(__name__)


def ext_pillar(minion_id, pillar, command):
    '''
    Execute a command and read the output as JSON
    '''
    log.debug(command)
    log.debug(minion_id)
    try:
        cmd = ' '.join([command, minion_id])
        popen = subprocess.Popen( cmd,
                                 shell=True,
                                 stdout=subprocess.PIPE)
        outs, errs = popen.communicate()
        retCode = popen.poll()
        assert(retCode == 0)
        return json.loads(outs)
    except Exception:
        log.critical(
                'JSON data from {0} failed to parse'.format(command)
                )
        return {}
