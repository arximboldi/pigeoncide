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

from tree import AutoTree, AutoTreeTraits
from observer import make_observer
from singleton import Singleton
from arg_parser import OptionBase
from error import *

class ConfError (BaseError):
    pass

ConfSubject, ConfListener = \
    make_observer (['conf_change',
                    'conf_nudge',
                    'conf_new_child',
                    'conf_del_child'],
                   'Conf')

class OptionConf (OptionBase):

    def __init__ (self, conf, func = str):
        self.conf = conf
        self.func = func

    def parse_with (self, arg):
        self.conf.value = self.func (arg)
        return True

class NullBackend:

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

    def _attach_on (self, node):
        pass

    def _detach_from (self, node):
        pass

class ConfNode (ConfSubject, AutoTree):
    
    def __init__ (self, name='', auto_tree_traits = AutoTreeTraits):
        AutoTree.__init__ (self, auto_tree_traits)
        ConfSubject.__init__ (self)
        self.rename (name)
        self._val = None
        self._backend = NullBackend ()

    def parent (self):
        return self._parent

    def default (self, val):
        if self._val is None:
            self._val = val

    def set_value (self, val):
        self._val = val
        self.on_conf_change (self)
        return self

    def get_value (self):
        return self._val

    def load (self, overwrite = False):
        self._backend._do_load (self, overwrite)

    def save (self):
        self._backend._do_save (self)
    
    def set_backend (self, be):
        if not self._test_empty_parent_be ():
            raise ConfError ("Can not set backend to owned nodes")
        else:
            self._backend._detach_from (self)   
            self._set_backend (be)
            self._backend._attach_on (self)
        
    def get_backend (self):
        return self._backend

    def nudge (self):
        self.on_conf_nudge (self)
        self._backend._handle_conf_nudge (self)

    def _handle_tree_new_child (self, child):
        child._backend = self._backend
        self._backend._handle_conf_new_node (child)
        self.on_conf_new_child (child)
        
    def _handle_tree_del_child (self, child):
        self._backend._handle_conf_del_node (child)
        self.on_conf_del_child (child)
        
    def _set_backend (self, be):
        def assign (self):
            self._backend = be
        self.dfs_preorder (assign)

    def _test_empty_parent_be (self):
        return self._parent is None or \
               (self._backend.__class__ is NullBackend and
                self._parent._test_empty_parent_be ())
    
    backend = property (get_backend, set_backend)
    value = property (get_value, set_value)

class GlobalConf (ConfNode):

    __metaclass__ = Singleton

    class Traits (AutoTreeTraits):
        child_cls = ConfNode
        
    def __init__ (self):
        ConfNode.__init__ (self, '', GlobalConf.Traits)
