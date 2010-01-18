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

"""
The Entity and all related classes provide means to handle the
combinatorial explosion of design decissions related to game Entities
using Python's mixins capability.

This way we can provide small pieces of incomplete classes that, when
combined together via inheritance, automatically build a new
class. The 'base.meta.mixin' function comes very handy to dynamically
build such mixins.

Some entities require some 'management' functionality, for such
reason, those must provide a EntityManager counterpart mixin.
"""

from pandac.PandaModules import Vec3

from core.task import Task
import weakref
from base.util import Selfable


class EntityManager (Selfable):

    def _add_entity (self, ent):
        pass

    def _del_entity (self, ent):
        pass


class Entity (object):

    def __init__ (self, entities = None, *a, **k):
        super (Entity, self).__init__ (*a, **k)
        self._hpr = Vec3 ()
        self._position = Vec3 ()
        self._entities = weakref.ref (entities)
        entities._add_entity (self)

    @property
    def entities (self):
        return self._entities ()
        
    def set_position (self, pos):
        self._position = pos

    def set_hpr (self, hpr):
        self._hpr = hpr

    def set_scale (self, scale):
        self._scale = scale

    def get_position (self):
        return self._position

    def get_hpr (self):
        return self._hpr

    def get_scale (self):
        return self._scale

    def dispose (self):
        self.entities._del_entity (self)

    position = property (get_position, lambda self, x: self.set_position (x))
    hpr      = property (get_hpr,      lambda self, x: self.set_hpr (x))
    scale    = property (get_scale,    lambda self, x: self.set_scale (x))


class DelegateEntity (Entity):

    def __init__ (self, delegate = None, *a, **k):
        super (DelegateEntity, self).__init__ (*a, **k)
        self.delegate = delegate
        
    def set_position (self, pos):
        super (DelegateEntity, self).set_position (pos)
        self.delegate.set_position (pos)
        
    def set_hpr (self, hpr):
        super (DelegateEntity, self).set_hpr (hpr)
        self.delegate.set_hpr (hpr)
                
    def set_scale (self, scale):
        super (DelegateEntity, self).set_scale (scale)
        self.delegate.set_scale (scale)

    def dispose (self):
        self.delegate.dispose ()
        super (DelegateEntity, self).dispose ()
        
    position = property (lambda self:    self.delegate.get_position (),
                         lambda self, x: self.set_position (x))
    hpr      = property (lambda self:    self.delegate.get_hpr (),
                         lambda self, x: self.set_hpr (x))
    scale    = property (lambda self:    self.delegate.get_scale (),
                         lambda self, x: self.set_scale (x))

