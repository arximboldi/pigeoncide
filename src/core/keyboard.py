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

from base.sender import Receiver
from base.util import flip_dict
from error import CoreError
from task import Task

class AlreadyMappedError (CoreError):
    pass

class KeyboardMap (Receiver):

    DOWN = 0
    UP   = 1

    def __init__ (self, keys = None, *a, **k):
        super (KeyboardMap, self).__init__ (*a, **k)

        if keys is None:
            self._map = {}
        else:
            self._map = flip_dict (keys)

    def assoc (self, action, key):
        if key in self._map:
            raise AlreadyMappedError (self._map [key])
        self._map [key] = action

    def unassoc (self, key):
        del self._map [key]

    def receive (self, ev, *a, **k):
        if ev in self._map:
            getattr (self, self._map [ev]) (
                self, UP if len (ev) > 3 and ev [-3:] == 'up' else DOWN)


class KeyboardTask (KeyboardMap, Task):

    def __init__ (self, *a, **k):
        super (KeyboardTask, self).__init__ (*a, **k)
        self._running = {}
        
    def receive (self, ev, *a, **k):
        if len (ev) > 3 and ev [-3:] == '-up' and ev [:-3] in self._running:
            del self._running [ev [:-3]]
        elif ev in self._map:
            self._running [ev] = getattr (self, self._map [ev])

    def update (self, dt):
        for f in self._running.itervalues ():
            f (dt)
