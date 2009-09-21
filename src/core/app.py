#
#  Copyright (C) 2009 Juan Pedro Bolivar Puente, Alberto Villegas Erce
#  
#  This file is part of Pigeoncide.
#
#  Pigeoncide is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  Pigeoncide is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import os.path

from xml_conf import *
from conf import *
from log import *
from arg_parser import *

class AppSuccess (Exception):
    pass

class AppBase:

    GLOBAL      = True
    
    NAME        = os.path.basename (sys.argv[0])
    VERSION     = ''
    DESCRIPTION = ''
    AUTHOR      = ''
    COPYRIGHT   = ''

    LICENSE     = \
"""\
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
"""

    USAGE       = \
"""\
Usage: %(program)s [options]
"""

    # TODO: Automatic formatting
    OPTIONS     = \
"""\
Options:
  -h, --help              Display this information.
  -v, --version           Display program version.
"""

    def prepare (self, argparser):
        pass

    def execute (self, args):
        pass

    def release (self):
        pass

    def run_and_exit (self):
        sys.exit (self.run ())
        
    def run (self):        
        if self.GLOBAL:
            GlobalConf ().rename (self.NAME)
            GlobalLog ().rename (self.NAME)
            GlobalLog ().add_listener (StdLogListener ())
        
        args = ArgParser ()
        args.add ('h', 'help', OptionFunc (self.print_help))
        args.add ('v', 'version', OptionFunc (self.print_version)) 

        self.prepare (args)

        try:
            args.parse (sys.argv)
            ret_val = self.execute (args.get_free_args ())
        except AppSuccess, e:
            ret_val = os.EX_OK
        except LoggableError, e:
            e.log ()
            ret_val = e.get_code ()
        except Exception, e:
            log (__name__, LOG_FATAL, "Unexpected error:\n" + e.message)
            ret_val = os.EX_SOFTWARE
        
        self.release ()

        return ret_val
        
    def print_help (self):
        print self.DESCRIPTION
        print self.USAGE % { "program" : self.NAME}
        print self.OPTIONS
        
        raise AppSuccess ()

    def print_version (self):
        print self.NAME, self.VERSION
        print
        print self.COPYRIGHT
        print self.LICENSE
        print "Written by", self.AUTHOR
        
        raise AppSuccess ()
    
    def get_config_folder (self):
        return os.path.join (os.environ ['HOME'], '.' + self.name)
    
    def get_data_folder (self):
        return os.path.join (['data'])
