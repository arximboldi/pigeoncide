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

from functools import partial
from weakref import *
from util import *
from meta import *

class Slot (object):

    def __init__ (self, func):
        self.func = func

    def __call__ (self, *args, **kw):
        return self.func (*args, **kw)

    def _handle_connect (self, signal):
        pass

    def _handle_disconnect (self, signal):
        pass


class CleverSlot (Slot):

    def __init__ (self, func):
        Slot.__init__ (self, func)
        self._signals = []

    def _handle_connect (self, signal):
        self._signals.append (ref (signal))

    def _handle_disconnect (self, signal):
        self._signals = remove_if (lambda x : x () == signal, self._signals)

    def disconnect (self):
        while len (self._signals) > 0:
            if self._signals [0] ():
                self._signals [0] ().disconnect (self)

    @property
    def count (self):
        return len (self._signals)


class Signal (object):

    def __init__ (self):
        self._slots = []

    def __del__ (self):
        for slot in self._slots:
            slot._handle_disconnect (self)
       
    def connect (self, slot):
        if not isinstance (slot, Slot): 
            slot = Slot (slot)

        if not slot in self._slots:
            self._slots.append (slot)
            slot._handle_connect (self)
        
        return slot

    def disconnect (self, slot):
        if isinstance (slot, Slot):
            slot._handle_disconnect (self)
            self._slots.remove (slot)
        else:
            self._disconnect_func (slot)
    
    def _disconnect_func (self, func):
        def pred (slot):
            if slot.func == func:
                slot._handle_disconnect (self)
                return True
            return False
            
        self._slots = remove_if (pred, self._slots)
    
    def notify (self, *args, **kw):
        for slot in self._slots:
            slot (*args, **kw)
    
    def fold (self, folder, ac = None):
        def executor (ac, func):
            return folder (ac, func ())
            
        if ac is None:
            ac = self._slots[0] ()
            return reduce (executor, self._slots [1:], ac)
        else:    
            return reduce (executor, self._slots, ac)
    
    def __iadd__ (self, slot):
        self.connect (slot)
        return self
        
    def __call__ (self, *args, **kw):
        self.notify (*args, **kw)
    
    def clear (self):
        del self._slots [:]

    @property
    def count (self):
        return len (self._slots)


class Slotable (object):

    def __init__ (self):
         self._slots = []

    def disconnect (self):
        for s in self._slots:
            s.disconnect ()


@instance_decorator
def slot (obj, func):
    s = CleverSlot (lambda *a, **k: func (obj, *a, **k))
    if isinstance (obj, Slotable):
        obj._slots.append (s)
    return s


@instance_decorator
def signal (obj, func):    
    class ExtendedSignal (Signal):
        def __call__ (self, *args, **kws):
            res = func (obj, *args, **kws)
            Signal.__call__ (self, *args, **kws)
            return res

    return ExtendedSignal ()

@instance_decorator
def signal_before (obj, func):
    class ExtendedSignalBefore (Signal):
        def __call__ (self, *args, **kws):
            Signal.__call__ (self, *args, **kws)
            res = func (obj, *args, **kws)
            return res
        
    return ExtendedSignalBefore ()


