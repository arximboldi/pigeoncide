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

import sys
from core.arg_parser import *

def print_help ():
    print "This is the help"
    exit (0)

def print_version ():
    print "This is the version"
    exit (0)

if __name__ == '__main__':
    opt_width = OptionWith (int, 800)
    opt_height = OptionWith (int, 600)

    args = ArgParser ()
    
    args.add ('h', 'help', OptionFunc (print_help))
    args.add ('v', 'version', OptionFunc (print_version))
    args.add ('H', 'height', opt_height)
    args.add ('W', 'width', opt_width)

    args.parse (sys.argv)

    print "Running with resolution: ", opt_width.value, "x", opt_height.value

