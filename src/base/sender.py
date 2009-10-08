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

class Sender (Source):

    def __init__ (self):
        self._receivers = []

    def __del__ (self):
        for receiver in self._receivers:
            receiver.handle_disconnect (self)

    def connect (self, receiver):
        if not receiver in self._receivers:
            receiver.handle_connect (self)
            self._receivers.append (receiver)

    def disconnect (self, receiver):
        self._receivers.remove (receiver)
        receiver.handle_disconnect (self)
        
    def send (self, signal_name, *args, **kws):
        for f in self._receivers:    
            f.receive (signal_name, *args, **kws)

    def clear (self):
        for receiver in self._receivers:
            receiver.handle_disconnect (self)
        del self._receivers [:]

    @property
    def receiver_count (self):
        return len (self._receivers)
