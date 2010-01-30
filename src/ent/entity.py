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
from base.log import get_log

_log = get_log (__name__)

class EntityManager (Selfable):

    def __init__ (self, *a, **k):
        super (EntityManager, self).__init__ (*a, **k)
        self.entities = []
    
    def dispose (self):
        while self.entities:
            self.entities [0].dispose ()
            
    def _add_entity (self, ent):
        self.entities.append (ent)

    def _del_entity (self, ent):
        self.entities.remove (ent)


class Entity (object):

    def __init__ (self, entities = None, *a, **k):
        _log.debug ("Creating entity: %s" % self)
        super (Entity, self).__init__ (*a, **k)
        self._entities = weakref.ref (entities)
        entities._add_entity (self)
                
    @property
    def entities (self):
        return self._entities ()
    
    def dispose (self):
        _log.debug ("Disposing entity: %s" % self)
        self.entities._del_entity (self)
        
    
class DelegateEntity (Entity):

    def __init__ (self,
                  delegate = None,
                  entities = None,
                  *a, **k):
        if entities == None:
            entities = delegate.entities
        super (DelegateEntity, self).__init__ (entities = entities,
                                               *a, **k)
        self.delegate = delegate
    
    def dispose (self):
        # FIXME: If I do this I break decorators, what should I do?
        # self.delegate.dispose ()
        super (DelegateEntity, self).dispose ()


class SpatialEntity (Entity):

    def __init__ (self, *a, **k):
        super (SpatialEntity, self).__init__ (*a, **k)
        self._hpr = Vec3 ()
        self._position = Vec3 ()
            
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

    position = property (get_position, lambda self, x: self.set_position (x))
    hpr      = property (get_hpr,      lambda self, x: self.set_hpr (x))
    scale    = property (get_scale,    lambda self, x: self.set_scale (x))


class DelegateSpatialEntity (DelegateEntity):
        
    def set_position (self, pos):
        self.delegate.set_position (pos)
        
    def set_hpr (self, hpr):
        self.delegate.set_hpr (hpr)
                
    def set_scale (self, scale):
        self.delegate.set_scale (scale)

    def get_position (self):
        return self.delegate.get_position ()
        
    def get_hpr (self):
        return self.delegate.get_hpr ()
                
    def get_scale (self):
        return self.delegate.get_scale ()
        
    position = property (get_position, set_position)
    hpr      = property (get_hpr,      set_hpr)
    scale    = property (get_scale,    set_scale)

"""
TODO:
Building the delegates has proven to be a bit... boring. Maybe using
base.proxy and some meta-programming magic we can make all this much
much easier.
"""

