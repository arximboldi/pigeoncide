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

from base.log import get_log
from base.signal import Signal


_log = get_log (__name__)

class EventManager (object):

    def __init__ (self):
        self._forwarders = []
        self._events = {}
        self.quiet = False
        
    def notify (self, name, *args, **kw):
        if not self.quiet:
            if name in self._events:
                self._events [name].notify (*args, **kw)
            else:
                self._forward (name, *args, **kw)

    def connect (self, name, slot):
        return self.event (name).connect (slot)
    
    def event (self, name):
        if name in self._events:
            return self._events [name]

        _log.debug ('Creating event: ' + name)
        signal = Signal ()
        signal += lambda *a, **k: self._forward (name, *a, **k)
        self._events [name] = signal
        return signal

    def add_forwarder (self, forwarder):
        self._forwarders.append (forwarder)

    def del_forwarder (self, forwarder):
        self._forwarders.remove (forwarder)

    @property
    def forwarder_count (self):
        return len (self._forwarders)

    def clear (self, name = None):
        if name:
            del self._events [name]
        else:
            self._events.clear ()
    
    def _forward (self, event, *args, **kw):
        for f in self._forwarders:
            f.notify (event, *args, **kw)
    
    
