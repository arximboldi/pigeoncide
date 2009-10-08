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

from observer import *
from tree import *
from singleton import Singleton
import sys

LogSubject, LogListener = \
    make_observer (['on_message'], 'Log')

LOG_FATAL   = 10, "fatal"
LOG_ERROR   = 8,  "error"
LOG_WARNING = 6,  "warning"
LOG_INFO    = 4,  "info"
LOG_DEBUG   = 2,  "debug"

class StdLogListener (LogListener):

    def __init__ (self,
                  level = LOG_INFO,
                  info_out = sys.stdout,
                  error_out = sys.stderr):
        self.level = level
        self.info_output = info_out
        self.error_output = error_out

    def on_message (self, node, level, msg):
        if level >= self.level:
            out = self.info_output if level <= LOG_INFO else self.error_output
            out.write ('[' + node.get_path_name () + '] ' +
                       level[1].upper () + ': '
                       + msg + '\n')
    
class LogNode (AutoTree, LogSubject):

    def __init__ (self, auto_tree_traits = AutoTreeTraits):
        AutoTree.__init__ (self, auto_tree_traits)
        LogSubject.__init__ (self)

    def log (self, level, msg):
        curr = self
        while curr:
            curr.on_message (self, level, msg)
            curr = curr.parent ()

    def info (self, msg):
        self.log (LOG_INFO, msg)

    def warning (self, msg):
        self.log (LOG_WARNING, msg)

    def error (self, msg):
        self.log (LOG_ERROR, msg)

    def fatal (self, msg):
        self.log (LOG_FATAL, msg)

    def debug (self, msg):
        self.log (LOG_DEBUG, msg)

    
class GlobalLog (LogNode):

    __metaclass__ = Singleton

    class Traits (AutoTreeTraits):
        child_cls = LogNode
        
    def __init__ (self):
        LogNode.__init__ (self, GlobalLog.Traits)

def log (path, level, msg):
    GlobalLog ().path (path).log (level, msg)

def get_log (path):
    return GlobalLog ().path (path)

