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

class AutoTreeTraits:
    name_type = str
    separator = '.'
    child_cls = None

class AutoTree:
    
    def __init__ (self, traits = AutoTreeTraits):
        self._traits = traits
        self._parent = None
        self._childs = {}
        self._name   = traits.name_type ()
        
    def get_child (self, name):
        try:
            child = self._childs [name]
        except KeyError:
            if self._traits.child_cls:
                child = self._tratis._child_cls ()
            else:
                child = self.__class__ ()
            self.adopt (child, name)
        
        return child
    
    def get_path (self, path_name):
        path = str.split (path_name, self._traits.separator)
        return reduce (AutoTree.get_child, path, self)
    
    def get_name (self):
        return self._name

    def get_path_name (self):
        return self._traits.separator.join (self.get_path_list ())

    def get_path_list (self, base = None):
        if base is None:
            base = []
            
        if self._parent:
            base = self._parent.get_path_list (base)
            base.append (self._name)
            return base
        else:
            base.append (self._name)
            return base
    
    def get_parent (self):
        return self._parent

    def adopt (self, child, name):
        old_parent = child.get_parent ()
        if old_parent:
            old_parent.remove (child.get_name ())

        child._parent = self
        child._name   = name
        self._childs [name] = child
        self._handle_tree_new_child (child)

        return child
    
    def remove (self, name):
        child = self._childs [name]
        self._handle_tree_del_child (child)
        del self._childs [name]
        child.parent = None
        child.name = self._traits.name_type ()

        return child

    def rename (self, name):
        if (self._parent):
            del self._parent._childs [self._name]
            self._parent._childs [name] = self
        self._name = name

    def dfs_preorder (self, func):
        func (self)
        for child in self._childs.values ():
            child.dfs_preorder (func)

    def dfs_postorder (self, func):
        for child in self._childs.values ():
            child.dfs_postorder (func)
        func (self)

    def childs (self):
        return self._childs.values ()
    
    def _handle_tree_new_child (self, child):
        pass
    
    def _handle_tree_del_child (self, child):
        pass
