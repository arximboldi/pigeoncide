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

from connection import *

class Receiver (Destiny):

    def receive (self, message, *args, **kws):
        if not hasattr (self, message):
            raise AttributeError ('Uncaugh message: ' + message)
        return getattr (self, message) (*args, **kws)

class Sender (Container):

    def send (self, signal_name, *args, **kws):
        for f in self._destinies:    
            f.receive (signal_name, *args, **kws)
