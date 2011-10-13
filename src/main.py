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

import __builtin__
import weakref

# old_object = object
# class NewObject (old_object):
#     def __init__ (self, *a, **k):
#         print "Received args: ", a, k
#         super (NewObject, self).__init__ (*a, **k)

# object = NewObject
# __builtin__.object = object

from app.pigeoncide import PigeoncideApp

def pigeoncide_main ():    
    app = PigeoncideApp ()
    app.run_and_exit ()

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    pigeoncide_main ()
