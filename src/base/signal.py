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

from connection import *
from sender import *
from util import *
from meta import *
from proxy import *

class Slot (Destiny):

    def __init__ (self, func):
        super (Slot, self).__init__ ()
        self.func = func

    def __call__ (self, *args, **kw):
        return self.func (*args, **kw)


class Signal (Source):

    def __init__ (self):
        self._slots = []

    def __del__ (self):
        for slot in self._slots:
            slot.handle_disconnect (self)

    def connect (self, slot):
        if not isinstance (slot, Slot): 
            slot = Slot (slot)

        if not slot in self._slots:
            self._slots.append (slot)
            slot.handle_connect (self)
        
        return slot

    def disconnect (self, slot):
        if isinstance (slot, Slot):
            slot.handle_disconnect (self)
            self._slots.remove (slot)
        else:
            self._disconnect_func (slot)
        
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
        return self.notify (*args, **kw)
    
    def clear (self):
        for slot in self._slots:
            slot.handle_disconnect (self)
        del self._slots [:]

    @property
    def count (self):
        return len (self._slots)

    def _disconnect_func (self, func):
        def pred (slot):
            if slot.func == func:
                slot.handle_disconnect (self)
                return True
            return False
            
        self._slots = remove_if (pred, self._slots)


class AutoSignalSenderGet (Sender):

    def __getattribute__ (self, name):
        attr = object.__getattribute__ (self, name)
        if isinstance (attr, Signal):
            return SenderSignalProxy (attr, self, name)
        return attr


class AutoSignalSender (Sender):

    def __setattr__ (self, name, attr):
        if isinstance (attr, Signal):
            object.__setattr__ (self, name,
                                SenderSignalProxy (attr, self, name))
        else:
            object.__setattr__ (self, name, attr)        
        return attr


class SenderSignal (Signal):

    def __init__ (self, sender, message):
        super (SenderSignal, self).__init__ ()
        self._sender = sender
        self._signame = signame
    
    def notify (self, *args, **kws):
        super (SenderSignal, self).notify (self, *args, **kws)
        self._sender.send (message, *args, **kws)


class SenderSignalProxy (AutoProxy):
    
    def __init__ (self, signal, sender, signame):
        super (SenderSignalProxy, self).__init__ (signal)
        self._sender = sender
        self._signame = signame

    def __call__ (self, *args, **kws):
        self.notify (*args, **kws)

    def notify (self, *args, **kws):
        self.proxied.notify (*args, **kws)
        self._sender.send (self._signame, *args, **kws)


@instance_decorator
def slot (obj, func):
    s = mixin (Trackable, Slot) (lambda *a, **k: func (obj, *a, **k))
    if isinstance (obj, Tracker):
        obj.register_trackable (s)
    return s


@instance_decorator
def signal (obj, func):
    if isinstance (obj, Sender) and not \
       isinstance (obj, AutoSignalSenderGet):
        class ExtendedSignal (Signal):
            def notify (self, *args, **kws):
                res = func (obj, *args, **kws)
                obj.send (func.__name__, *args, **kws)
                Signal.notify (self, *args, **kws)
                return res
    else:
        class ExtendedSignal (Signal):
            def notify (self, *args, **kws):
                res = func (obj, *args, **kws)
                Signal.notify (self, *args, **kws)
                return res

    return ExtendedSignal ()


@instance_decorator
def signal_before (obj, func):
    if isinstance (obj, Sender) and not\
       isinstance (obj, AutoSignalSenderGet):
        class ExtendedSignalBefore (Signal):
            def notify (self, *args, **kws):
                obj.send (func.__name__, *args, **kws)
                Signal.notify (self, *args, **kws)
                res = func (obj, *args, **kws)
                return res
    else:
        class ExtendedSignalBefore (Signal):
            def notify (self, *args, **kws):
                Signal.notify (self, *args, **kws)
                res = func (obj, *args, **kws)
                return res
        
    return ExtendedSignalBefore ()


