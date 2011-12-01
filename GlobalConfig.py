'''
A module for globally sharing ConfigParser objects.

To create a new global configParser object:

  from GlobalConfig import *
  InitConfig()
  config = GetConfig()
  config.read(['my-config-file.conf'])

Once initialized, application code can obtain the configParser
object with:

  from GlobalConfig import GetConfig
  config = GetConfig()
  my_val = config.get('my_section','my_param')

For more information, see the Python module ConfigParser.

Part of the AT&T Statistical Dialog Toolkit (ASDT).

Jason D. Williams
jdw@research.att.com
www.research.att.com/people/Williams_Jason_D
'''

from ConfigParser import ConfigParser

_GLOBAL_CONFIG = None

def InitConfig():
    global _GLOBAL_CONFIG
    assert (_GLOBAL_CONFIG == None),'InitConfig has already been called.'
    _GLOBAL_CONFIG = ConfigParser()
    _GLOBAL_CONFIG.optionxform = str

def GetConfig():
    global _GLOBAL_CONFIG
    return _GLOBAL_CONFIG
