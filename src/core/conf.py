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

from tree import AutoTree
from observer import make_observer

ConfSubject, ConfListener = \
    make_observer ('Conf', ['conf_change',
                            'conf_nudge'])

class ConfBackend:

    def _handle_conf_new_node (self, node):
        pass

    def _handle_conf_del_node (self, node):
        pass

    def _handle_conf_change (self, node):
        pass

    def _handle_conf_nudge (self, node):
        pass

    def _do_load (self, node, overwrite):
        pass

    def _do_save (self, node):
        pass

class ConfNode (ConfSubject, AutoTree):

    backend = property (get_backend, set_backend)
    val = property (get_val, set_val)
    
    def __init__ (self):
        AutoTree.__init__ (self)
        ConfSubject.__init__ (self)
        self._val = None
        self._backend = ConfBackend ()

    def default (self, val):
        if self._val is None:
            self._val = val

    def set_val (self, val):
        self._val = val
        self.on_conf_change (self)
        return self

    def get_val (self, val):
        return self._val

    def load (self, overwrite = False):
        self._backend.do_load (self, overwrite)

    def save (self):
        self._backend.do_save (self)
    
    def set_backend (self, be):
        pass

    def get_backend (self):
        return self._backend

    def nudge (self):
        self.on_conf_nudge (self)
        self._backend._handle_conf_nudge (self)

    def _handle_tree_new_child (self, child):
        self._backend._handle_conf_new_child (child)

    def _handle_tree_del_child (self, child):
        self._backend._handle_conf_new_child (child)

