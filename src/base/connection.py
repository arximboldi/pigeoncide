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

from weakref import ref
from util import remove_if

class Source (object):

    def connect (self, destiny):
        pass

    def disconnect (self, destiny):
        pass


class Destiny (object):

    def handle_connect (self, source):
        pass

    def handle_disconnect (self, source):
        pass


class Container (Source):

    def __init__ (self, *a, **kw):
        super (Container, self).__init__ (*a, **kw)
        t = kw.get ('container_type', list)
        self._destinies = t ()

    def __del__ (self):
        for dest in self._destinies:
            dest.handle_disconnect (self)

    def connect (self, destiny):
        if destiny not in self._destinies:
            self._destinies.append (destiny)
            destiny.handle_connect (self)
        return destiny
    
    def disconnect (self, destiny):
        self._destinies.remove (destiny)
        destiny.handle_disconnect (self)

    def disconnect_if (self, predicate):
        def pred (dest):
            if predicate (dest):
                dest.handle_disconnect (self)
                return True
            return False
        
        self._destinies = remove_if (pred, self._destinies)

    def clear (self):
        for dest in self._destinies:
            dest.handle_disconnect (self)
        del self._destinies [:]

    @property
    def count (self):
        return len (self._destinies)


class Trackable (object):

    def __init__ (self, *a, **kw):
        super (Trackable, self).__init__ (*a, **kw)
        self._sources = []

    def handle_connect (self, source):
        self._sources.append (ref (source))

    def handle_disconnect (self, source):
        self._sources = remove_if (lambda x : x () == source, self._sources)

    def disconnect_sources (self):
        while len (self._sources) > 0:
            if self._sources [0] ():
                self._sources [0] ().disconnect (self)

    @property
    def source_count (self):
        return len (self._sources)


class Tracker (object):

    def __init__ (self):
         self._trackables = []

    def register_trackable (self, trackable):
        self._trackables.append (trackable)

    def disconnect_all (self):
        for t in self._trackables:
            t.disconnect_sources ()

    @property
    def trackable_count (self):
        return len (self._trackables)
