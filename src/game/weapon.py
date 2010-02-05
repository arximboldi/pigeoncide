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

from core import task
from core.util import to_rad, normalize
from phys import geom
import physics
import weakref
from pandac.PandaModules import Vec3
import math
import random

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

    weapon_sounds = [ 'snd/weapon-hit-wood.wav',
                      'snd/weapon-hit-metal.wav',
                      'snd/weapon-hit-lolly.wav',
                      'snd/weapon-hit-slightly-metallic.wav' ]
    weapon_swing  = [ 'snd/weapon-swing-1.wav',
                      'snd/weapon-swing-2.wav',
                      'snd/weapon-swing-3.wav',
                      'snd/weapon-swing-4.wav' ]
    
    weapon_model = ''

    weapon_hit_delay   = 1.0
    
    weapon_hit_speed   = 100.
    weapon_throw_speed = 100.
    
    weapon_position = Vec3 (0, 0, 0)
    weapon_hpr      = Vec3 (0, 0, 0)
    weapon_scale    = Vec3 (1, 1, 1)

    weapon_geom_owned = None
    weapon_geom_free  = None
    weapon_hit_radius = 7.

    def __init__ (self, *a, **k):
        super (WeaponEntity, self).__init__ (*a, **k)
        self._hit_time = {}
        self._timer = None
        self._owner        = None
        self._child_entity = None
        self._make_free_entity ()        
        self._hit_sounds   = map (self.entities.audio3d.loadSfx,
                                  self.weapon_sounds)
        self._swing_sounds = map (self.entities.audio3d.loadSfx,
                                  self.weapon_swing)
    
    def play_random_sound (self, sounds):
        snd = random.choice (sounds)
        px, py, pz = self._child_entity.position
        snd.set3dAttributes (px, py, pz, 0, 0, 0)
        snd.play ()
    
    def dispose (self):
        if self._child_entity:
            self._child_entity.dispose ()
        super (WeaponEntity, self).dispose ()

    def set_position (self, pos):
        super (WeaponEntity, self).set_position (pos)
        self._child_entity.position = pos

    def _make_free_entity (self, *a, **k):
        _log.debug ("Creating free entity.")
        g = self.weapon_geom_free if self.weapon_geom_free \
            else geom.sphere (self.weapon_hit_radius)
        self._make_child_entity (FreeWeaponEntity,
                                 geometry = g,
                                 category = physics.weapon_category,
                                 *a, **k)
        self._child_entity.on_collide += self.on_touch
        
    def _make_owned_entity (self, *a, **k):
        _log.debug ("Creating owned entity")
        g = self.weapon_geom_owned if self.weapon_geom_owned \
            else geom.sphere (self.weapon_hit_radius)
        
        self._make_child_entity (OwnedWeaponEntity,
                                 geometry = g,
                                 collide  = physics.pigeon_category,
                                 category = physics.null_category,
                                 *a, **k)
        
    def _make_child_entity (self, entity_cls, scale_factor = None, *a, **k):
        scale = self.weapon_scale
        if scale_factor:
            cx, cy, cz = self.weapon_scale
            sx, sy, sz = scale_factor
            scale = Vec3 (cx/sx, cy/sy, cz/sz)
                
        entity = entity_cls (entities = self.entities,
                             model = self.weapon_model,
                             *a, **k)

        px, py, pz = self.weapon_position
        sx, sy, sz = scale
        position   = Vec3 (px*sx, py*sy, pz*sz) 
        
        entity.model_hpr = self.weapon_hpr
        entity.model_scale = scale
        entity.model_position = position
        entity.physics_hpr =  self.weapon_hpr
        entity.physics_position = position

        entity.enable_collision ()
        self._child_entity = entity
        _log.debug ("Done creating entity")
        
    @weak_slot
    def on_touch (self, ev, me, other):
        if isinstance (other, WeaponOwner):
            self.set_owner (other)

    @weak_slot
    def on_hit (self, ev, me, other):
        """ Make sure that this gets executed on hittable only... """
        _log.debug ("A weapon %s hitted a %s." % (str (me), str (other)))
        if self._timer.elapsed - other.hit_time > self.weapon_hit_delay:
            self.play_random_sound (self._hit_sounds)
            direction = normalize (other.position - self._owner.position)
            direction.setZ (math.sin (math.pi / 4.))
            other.hit_time = self._timer.elapsed
            self.entities.tasks.add (task.sequence (
                task.delay (),
                task.run (
                    lambda: other.set_linear_velocity (normalize (direction) *
                                                       self.weapon_hit_speed))))
            other.on_hit (self)
    
    def do_update (self, timer):
        super (WeaponEntity, self).do_update (self)
        self._timer = timer
                
    def start_hitting (self):
        if self._owner:
            self._child_entity.on_collide += self.on_hit
            self.play_random_sound (self._swing_sounds)
            
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
                self._make_owned_entity (parent_node = joint,
                                         scale_factor = owner.model_scale)
                
            if self._owner:
                h, p, r = self._owner.hpr
                h = to_rad (h - 90)
                
                direction = Vec3 (math.cos (h), math.sin (h), 0)
                self._make_free_entity ()
                self._child_entity.position = old_position + direction * 5
                self._child_entity.hpr      = old_hpr
                self._child_entity.set_linear_velocity (direction *
                                                        self.weapon_throw_speed)
                self._owner.del_weapon (self)
                self._owner.last_weapon_time = self._timer.elapsed
                
            self._owner = owner

    def get_owner (self):
        return self._owner

    owner = property (get_owner, set_owner)


class BaseballBat (WeaponEntity):

    weapon_model    = 'obj/baseball-bat.egg'

    weapon_geom_free = geom.box (5, 5, 1)
    weapon_scale     = Vec3 (.3, .3, .3)
    weapon_position  = Vec3 (-2*.3, -5*.3, 1*.3)
    weapon_hpr       = Vec3 (0, -90, 0)


class Lollypop (WeaponEntity):

    weapon_model    = 'obj/lollypop.egg'

    weapon_geom_free = geom.box (5, 5, 1)
    weapon_scale     = Vec3 (.3, .3, .3)
    weapon_position  = Vec3 (-2*.3, -5*.3, 1*.3)
    weapon_hpr       = Vec3 (0, -90, 0)


class RollingPin (WeaponEntity):

    weapon_model    = 'obj/rolling-pin.egg'

    weapon_geom_free = geom.box (5, 5, 1)
    weapon_scale     = Vec3 (.3, .3, .3)
    weapon_position  = Vec3 (-2*.3, -5*.3, 1*.3)
    weapon_hpr       = Vec3 (0, -90, 0)
