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

from direct.showbase.ShowBase import ShowBase

from base.signal import Signal
from base.sender import Sender, Receiver
from base.log import get_log
from base.util import flip_dict
from error import CoreError
from task import Task
import os

_log = get_log (__name__)

class AlreadyMappedError (CoreError):
    pass

class EventMap (Receiver):

    DOWN = 0
    UP   = 1

    def __init__ (self, eventmap = None, *a, **k):
        super (EventMap, self).__init__ (*a, **k)

        if eventmap is None:
            self._map = {}
        else:
            self._map = flip_dict (eventmap)

    def assoc (self, action, key):
        if key in self._map:
            raise AlreadyMappedError (self._map [key])
        self._map [key] = action

    def unassoc (self, key):
        del self._map [key]

    def unassoc_action (self, action):
        for k, a in dict (self._map).iteritems ():
            if a == action:
                del self._map [k]
    
    def receive (self, ev, *a, **k):
        if ev in self._map:
            getattr (self, self._map [ev]) (
                self, UP if len (ev) > 3 and ev [-3:] == 'up' else DOWN)


class KeyboardTask (EventMap, Task):

    DOWN_TAG = '_down'
    UP_TAG   = '_up'
    
    def __init__ (self, *a, **k):
        super (KeyboardTask, self).__init__ (*a, **k)
        self._running = {}
        
    def receive (self, ev, *a, **k):
        
        if len (ev) > 3 and ev [-3:] == '-up':
            ev = ev [:-3]
            if ev in self._running:
                del self._running [ev]
            if ev in self._map:
                attrname = self._map [ev]
                if is_key_event (ev):
                    attrname += self.UP_TAG
                if hasattr (self, attrname):
                    getattr (self, attrname) ()

        elif ev in self._map:
            attrname = self._map [ev]
            if is_key_event (ev):
                if hasattr (self, attrname):
                    self._running [ev] = getattr (self, attrname)
                attrname += self.DOWN_TAG
            if hasattr (self, attrname):
                getattr (self, attrname) (*a, **k)
            
    def do_update (self, timer):
        super (KeyboardTask, self).do_update (timer)
        for f in self._running.itervalues ():
            f (timer)


need_mouse_hack = os.name == 'posix'

class MouseTask (Task):

    def __init__ (self, device = 0, *a, **k):
        super (MouseTask, self).__init__ (*a, **k)
        self.device = device
        self._last_x  = -1
        self._last_y  = -1
        self._is_init = False
        self._reset_mouse ()
        self.on_mouse_move = Signal ()
        
    def _reset_mouse (self):
        if not need_mouse_hack:
            return
        
        window = base.win
        prop = window.getProperties ()
        if prop.hasSize ():
            new_x = prop.getXSize () / 2
            new_y = prop.getYSize () / 2
            window.movePointer (0, new_x, new_y)
            self._last_x = new_x 
            self._last_y = new_y
            self._is_init = True
    
    def do_update  (self, timer):
        super (MouseTask, self).do_update (timer)

        if base.win.hasPointer (0):
            p = base.win.getPointer (0)
            x = p.getX ()
            y = p.getY ()
            delta_x = x - self._last_x
            delta_y = y - self._last_y
            if self._is_init and \
                (abs (delta_x) > 0 or abs (delta_y) > 0):
                self.on_mouse_move (delta_x, delta_y)
            self._last_x = x
            self._last_y = y
            self._is_init = True
            self._reset_mouse ()


panda_special_keys = set ([
    "escape",
    "f1", "f2", "f3", "f4", "f5", "f6",
    "f7", "f8", "f9", "f10", "f11", "f12",
    "print_screen", "scroll_lock", "backspace",
    "insert", "home", "page_up", "num_lock",
    "tab",  "delete", "end", "page_down",
    "caps_lock", "enter",
    "arrow_left", "arrow_up", "arrow_down", "arrow_right",
    "shift", "lshift", "rshift",
    "control", "alt", "lcontrol",
    "lalt", "space", "ralt", "rcontrol",
    "mouse1", "mouse2", "mouse3"
    ])

def is_key_event (ev):
    
    if len (ev) < 7 or ev [:6] != 'panda-':
        return False

    if len (ev) == 7:
        return True

    return ev [6:] in panda_special_keys
