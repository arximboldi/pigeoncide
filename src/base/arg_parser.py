#
#  Copyright (C) 2009 Juan Pedro Bolivar Puente, Alberto Villegas Erce
#  
#  This file is part of Pidgeoncide.
#
#  Pidgeoncide is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  Pidgeoncide is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from error import *

class ArgParserError (BaseError):

    def __init__(self):
        BaseError.__init__(self, "Unknown argument parsing error")

class UnknownArgError (ArgParserError):

    def __init__(self, arg):
        BaseError.__init__(self, "Unknown arg: " + arg)

class OptionBase:

    def parse_with(self, arg):
        return False

    def parse_flag(self):
        return False

class OptionWith (OptionBase):

    def __init__(self, func, default=None):
        self.value = default
        self._func = func

    def parse_with(self, arg):
        self.value = self._func (arg)
        return True

class OptionFlag (OptionBase):

    def __init__(self, default=False):
        self.value = False

    def parse_flag(self):
        self.value = True
        return True
         
class OptionFunc (OptionBase):

    def __init__(self, func):
        self._func = func
    
    def parse_flag(self):
        self._func ()
        return True
     
class ArgParser:

    def __init__(self):
        self._free_args = []
        self._long_ops = {}
        self._short_ops = {}

    def get_free_args (self):
        return self._free_args
    
    def add (self, shortarg, longarg, option):
        if shortarg in self._short_ops:
            self._short_ops[shortarg].append(option)
        else:
            self._short_ops[shortarg] = [option]
            
        if longarg in self._long_ops:
            self._long_ops[longarg].append(option)
        else:
            self._long_ops[longarg] = [option]
        
        return self
    
    def parse (self, argv):
        i = 1
        self._argc = len (argv)
        self._argv = argv

        try:
            while i < self._argc:
                if len (argv[i]) > 1 and argv[i][0] == '-':
                    if argv[i][1] == '-':
                        i = self._parse_long (i)
                    else:
                        i = self._parse_short (i)
                else:
                    self._free_args.append (arg)
        except KeyError, e:
            raise UnknownArgError (e.message)

    def _parse_long (self, i):
        arg = self._argv[i][2:]
        
        return reduce (self._parse_opt, self._long_ops[arg], i + 1)

    def _parse_short (self, i):
        arg = self._argv[i][1:]

        return reduce (self._parse_opt,
                       sum (map (self._short_ops.__getitem__, arg), []),
                       i + 1)

    def _parse_opt (self, i, opt):
        if i >= self._argc or not opt.parse_with (self._argv[i]):
            opt.parse_flag ()
            return i
        else:
            return i+1
