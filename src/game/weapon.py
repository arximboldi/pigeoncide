#
#  Copyright (C) 2010 Juan Pedro Bolivar Puente, Alberto Villegas Erce
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

from base.signal import signal
from base.log import get_log

from ent.entity import SpatialEntity, DelegateSpatialEntity, Entity
from ent.physical import StaticPhysicalEntity, DynamicPhysicalEntity
from ent.panda import RelativeModelEntity, ModelEntity
from ent.task import TaskEntity
from base.signal import weak_slot

from core.util import to_rad, normalize
from phys import geom
import physics
import weakref
from pandac.PandaModules import Vec3
import math


_log = get_log (__name__)


class Hittable (object):
    hit_time = 0.0
    on_hit   = signal ()

class OwnedWeaponEntity (
    StaticPhysicalEntity,
    RelativeModelEntity):
    pass

class FreeWeaponEntity (
    DynamicPhysicalEntity,
    ModelEntity):
    pass


class WeaponOwnerBase (Entity):
    
    weapon = None
    last_weapon_time = 0.0
    
    def add_weapon (self, weapon):
        if self.weapon:
            return False
        self.weapon = weakref.proxy (weapon)
        return True
    
    def del_weapon (self, weapon):
        self.weapon = None

class WeaponOwner (
    WeaponOwnerBase,
    SpatialEntity):
    pass

class DelegateWeaponOwner (DelegateSpatialEntity):

    @property
    def weapon (self):
        return self.delegate.weapon


class WeaponEntity (SpatialEntity, TaskEntity):

    weapon_model = ''

    weapon_hit_delay   = 1.0
    
    weapon_hit_force   = 10000.
    weapon_throw_force = 500.
    
    weapon_position = Vec3 (0, 0, 0)
    weapon_hpr      = Vec3 (0, 0, 0)
    weapon_scale    = Vec3 (0, 0, 0)

    weapon_geom_owned = None
    weapon_geom_free  = None
    weapon_hit_radius = 1000

    def __init__ (self, *a, **k):
        super (WeaponEntity, self).__init__ (*a, **k)
        self._hit_time = {}
        self._timer = None
        self._owner        = None
        self._child_entity = None
        self._make_free_entity ()
        
    def dispose (self):
        if self._child_entity:
            self._child_entity.dispose ()
        super (WeaponEntity, self).dispose ()

    def set_position (self, pos):
        super (WeaponEntity, self).set_position (pos)
        self._child_entity.position = pos

    def _make_free_entity (self, *a, **k):
        g = self.weapon_geom_free if self.weapon_geom_free \
            else geom.mesh (self.weapon_model, scale = self.weapon_scale)
        self._make_child_entity (FreeWeaponEntity,
                                 geom = g,
                                 category = physics.weapon_category,
                                 *a, **k)
        self._child_entity.on_collide += self.on_touch
        
    def _make_owned_entity (self, *a, **k):
        g = self.weapon_geom_owned if self.weapon_geom_owned \
            else geom.sphere (self.weapon_hit_radius)
        self._make_child_entity (OwnedWeaponEntity,
                                 geom = self.weapon_geom_owned,
                                 collide  = physics.pigeon_category,
                                 category = physics.null_category,
                                 *a, **k)
    
    def _make_child_entity (self, entity_cls, *a, **k):
        entity = entity_cls (entities = self.entities,
                             model = self.weapon_model,
                             *a, **k)
        entity.model_hpr = self.weapon_hpr
        entity.model_scale = self.weapon_scale
        entity.model_position = self.weapon_position
        entity.physics_hpr =  self.weapon_hpr
        entity.physics_position = self.weapon_position

        entity.enable_collision ()
        self._child_entity = entity

    @weak_slot
    def on_touch (self, ev, me, other):
        if isinstance (other, WeaponOwner):
            self.set_owner (other)

    @weak_slot
    def on_hit (self, ev, me, other):
        """ Make sure that this gets executed on hittable only... """
        _log.debug ("A weapon %s hitted a %s." % (str (me), str (other)))
        if self._timer.elapsed - other.hit_time > self.weapon_hit_delay:
            direction = normalize (other.position - self._owner.position)
            other.add_force (
                direction * self.weapon_hit_force * self._timer.delta)
            other.on_hit (self)
    
    def do_update (self, timer):
        super (WeaponEntity, self).do_update (self)
        self._timer = timer
                
    def start_hitting (self):
        if self._owner:
            self._child_entity.on_collide += self.on_hit

    def finish_hitting (self):
        if self._owner:
            self._child_entity.on_collide -= self.on_hit

    def may_take_weapon (self, owner):
        return owner and \
               self._timer.elapsed - owner.last_weapon_time > 1.0 and \
               owner.add_weapon (self)
    
    def set_owner (self, owner):
        if self._owner or self.may_take_weapon (owner):
            old_position = self._child_entity.position
            old_hpr      = self._child_entity.hpr
            
            self._child_entity.dispose ()    

            if owner:
                joint = owner.model.exposeJoint (None, 'modelRoot',
                                                 'Bip01_R_Finger0')
                self._make_owned_entity (parent_node = joint)
                cx, cy, cz = self._child_entity.model_scale
                sx, sy, sz = owner.model_scale
                self._child_entity.model_scale = Vec3 (cx/sx, cy/sy, cz/sz) 
                
            if self._owner:
                h, p, r = self._owner.hpr
                h = to_rad (h - 90)
                direction = Vec3 (math.cos (h), math.sin (h), 0)
                self._make_free_entity ()
                self._child_entity.position = old_position
                self._child_entity.hpr      = old_hpr
                # TODO: This is not affecting!
                self._child_entity.add_force (direction *
                                              self.weapon_throw_force /
                                              self._timer.delta)
                self._owner.del_weapon (self)
                self._owner.last_weapon_time = self._timer.elapsed
                
            self._owner = owner

    def get_owner (self):
        return self._owner

    owner = property (get_owner, set_owner)


class BaseballBat (WeaponEntity):

    weapon_model    = 'obj/baseball-bat.egg'

    weapon_free_geom = geom.capsule (5, 20)
    weapon_scale    = Vec3 (.3, .3, .3)
    weapon_position = Vec3 (-2, -5, 1)
    weapon_hpr      = Vec3 (0, -90, 0)
