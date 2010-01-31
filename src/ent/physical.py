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

from entity import *
from task import TaskEntity

from core.util import *
from core.task import TaskError

from pandac.PandaModules import *
import math

from phys.physics import Physics
import phys.mass as mass
import phys.geom as geom

from base.signal import Signal, weak_slot

default_category = 0x0001

class PhysicalEntityManager (EntityManager):

    _owns_physics = False
    
    def __init__ (self,
                  physics = None,
                  phys_events = None,
                  *a, **k):
        super (PhysicalEntityManager, self).__init__ (*a, **k)

        if physics:
            self.physics = physics
        else:
            self.physics = Physics (phys_events)
            self._owns_physics = True
        
        try:
            # TODO: Make mixin initialization order irrelevant
            self.tasks.add (self.physics)
        except TaskError, e:
            pass
        
    def dispose (self):
        super (PhysicalEntityManager, self).dispose ()
        if self._owns_physics:
            self.physics.dispose ()


class PhysicalEntityBase (SpatialEntity):

    _physical_position = Vec3 (0, 0, 0)
    _physical_hpr      = Vec3 (0, 0, 0)

    def __init__ (self,
                  entities = None,
                  geometry = geom.box (1, 1, 1),
                  category = default_category,
                  collide  = 0xffff,
                  *a, **k):
        super (PhysicalEntityBase, self).__init__ (
            entities = entities,
            *a, **k)
        self._geom = geometry (entities.physics.space)
        self._geom.setCategoryBits (category)
        self._geom.setCollideBits (collide)
        
        entities.physics.register (self._geom)
        
    def set_physical_position (self, pos):
        self._physical_position = pos

    def get_physical_position (self):
        return self._physical_position

    def set_physical_hpr (self, hpr):
        self._physical_hpr = hpr

    def get_physical_hpr (self):
        return self._physical_hpr
    
    @property
    def geom (self):
        return self._geom

    def enable_collision (self):
        if not hasattr (self, 'on_collide'):
            self.on_collide = Signal ()
            self.entities.physics.register_geom_callback (
                self._geom, self.on_collide, self)
            
    def disable_collision (self):
        del self.on_collide
        self.entities.physics.unregister_geom_callback (self._geom)

    def dispose (self):
        self.entities.physics.unregister (self._geom)
        if self._geom:
            self._geom.destroy ()
        super (PhysicalEntityBase, self).dispose ()

    physical_position = property (
        get_physical_position,
        lambda self, x: self.set_physical_position (x))
    physical_hpr      = property (
        get_physical_hpr,
        lambda self, x: self.set_physical_hpr (x))
        

class StaticPhysicalEntity (PhysicalEntityBase):

    def set_physical_position (self, pos):
        super (StaticPhysicalEntity, self).set_physical_position (pos)
        self._geom.setPosition (self._position + self._physical_position)

    def set_physical_hpr (self, hpr):
        super (StaticPhysicalEntity, self).set_physical_hpr (hpr)
        self._geom.setQuaternion (hpr_to_quat (self._position + hpr))
    
    def set_position (self, pos):
        super (StaticPhysicalEntity, self).set_position (pos)
        self._geom.setPosition (pos + self._physical_position)
        
    def set_hpr (self, hpr):
        super (StaticPhysicalEntity, self).set_hpr (hpr)
        self._geom.setQuaternion (hpr_to_quat (hpr + self._physical_hpr))

    def set_scale (self, scale):
        super (StaticPhysicalEntity, self).set_scale (scale)


class DynamicPhysicalEntity (PhysicalEntityBase, TaskEntity):

    def __init__ (self,
                  entities = None,
                  mass     = mass.box (1000, 1, 1, 1),
                  *a, **k):
        super (DynamicPhysicalEntity, self).__init__ (
            entities = entities,
            *a, **k)

        physics = entities.physics
        
        self._mass = OdeMass ()
        mass (self._mass)
        self._body = OdeBody (physics.world)
        self._body.setMass (self._mass)
        self._geom.setBody (self._body)
        
        self._updating = False

    def dispose (self):
        super (DynamicPhysicalEntity, self).dispose ()
        if self._body:
            self._body.destroy ()

    @property
    def mass (self):
        return self._mass.getMagnitude ()

    @property
    def body (self):
        return self._body

    def set_physical_position (self, pos):
        super (DynamicPhysicalEntity, self).set_physical_position (pos)
        self._body.setPosition (self._position + self._physical_position)

    def set_physical_hpr (self, hpr):
        super (DynamicPhysicalEntity, self).set_physical_hpr (hpr)
        self._body.setQuaternion (hpr_to_quat (self._position + hpr))

    def get_linear_velocity (self):
        return self._body.getLinearVel ()

    def set_linear_velocity (self, vel):
        self._body.setLinearVel (vel)

    def get_angular_velocity (self):
        return self._body.getAngularVel ()

    def set_angular_velocity (self, vel):
        self._body.setAngularVel (vel)

    def set_torque (self, torque):
        self._body.setTorque (torque)

    def set_force (self, force):
        self._body.setForce (force)

    def add_force (self, force):
        self._body.addForce (force)

    def add_torque (self, force):
        self._body.addTorque (force)

    def set_position (self, pos):
        super (DynamicPhysicalEntity, self).set_position (pos)
        if not self._updating:
            self._body.setPosition (self._physical_position + pos)
        
    def set_hpr (self, hpr):
        super (DynamicPhysicalEntity, self).set_hpr (hpr)
        if not self._updating:
            self._body.setQuaternion (hpr_to_quat (self._physical_hpr + hpr))

    def set_scale (self, scale):
        super (DynamicPhysicalEntity, self).set_scale (scale)
        # FIXME if not self._updating:
        # self._body.setScale (scale)

    def disable_physics (self):
        self._body.disable ()
        
    def do_update (self, timer):
        super (DynamicPhysicalEntity, self).do_update (timer)

        pos = self._body.getPosition ()
        hpr = self._body.getQuaternion ()
        
        self._updating = True
        self.set_position (pos)        
        self.set_hpr (vec_to_hpr (hpr))
        self._updating = False

    linear_velocity = property (get_linear_velocity, set_linear_velocity)
    angular_velocity = property (get_angular_velocity, set_angular_velocity)


class DelegatePhysicalEntityBase (DelegateSpatialEntity):

    @property
    def geom (self):
        return self.delegate.geom

    @property
    def on_collide (self):
        return self.delegate.on_collide

    def enable_collision (self):
        return self.delegate.enable_collision ()

    def disable_collision (self):
        return self.delegate.disable_collision ()


class DelegateDynamicPhysicalEntity (DelegatePhysicalEntityBase):

    @property
    def body (self):
        return self.delegate.body

    @property
    def speed (self):
        return self.delegate.speed
    
    def add_force (self, force):
        self.delegate.add_force (force)

    def add_torque (self, torque):
        self.delegate.add_torque (torque)

    def set_force (self, force):
        self.delegate.set_force (force)

    def set_torque (self, torque):
        self.delegate.set_torque (torque)

    def get_linear_velocity (self):
        return self.delegate.linear_velocity

    def set_linear_velocity (self, vel):
        self.delegate.linear_velocity = vel

    def get_angular_velocity (self):
        return self.delegate.angular_velocity

    def set_angular_velocity (self, vel):
        self.delegate.angular_velocity = vel
    
    linear_velocity = property (get_linear_velocity, set_linear_velocity)
    angular_velocity = property (get_angular_velocity, set_angular_velocity)


class StandingPhysicalEntityBase (TaskEntity):
    """
    DynamicPhysicalEntity should be updated first. Take this into
    account when composing the mixin.
    """
    
    def __init__ (self, *a, **k):
        super (StandingPhysicalEntityBase, self).__init__ (*a, **k)
        self.angle = 0
        self.enable_collision ()
            
    def do_update (self, timer):
        self.update_standing ()
        super (StandingPhysicalEntityBase, self).do_update (timer)
    
    def update_standing (self):
        body = self.body
        hpr = body.getQuaternion ()
        # http://www.euclideanspace.com/maths/geometry/rotations/
        # conversions/angleToQuaternion/index.htm      
        body.setQuaternion (Quat (math.sin (self.angle / 2), 0, 0,
                                  math.cos (self.angle / 2)))
        body.setTorque (0, 0, 0)
        body.setAngularVel (0, 0, 0)


class StandingPhysicalEntity (
    StandingPhysicalEntityBase,
    DynamicPhysicalEntity):
    pass


class StandingPhysicalEntityDecorator (
    DelegateDynamicPhysicalEntity,
    StandingPhysicalEntityBase):
    pass


class DelegateStandingPhysicalEntity (DelegateDynamicPhysicalEntity):

    def _set_angle (self, angle):
        self.delegate.angle = angle

    def _get_angle (self):
        return self.delegate.angle

    angle = property (_get_angle, _set_angle)


class OnFloorEntity (PhysicalEntityBase, TaskEntity):
    """
    TODO: Move to a different module.
    """

    on_floor_delay = 0.3
    
    def __init__ (self, *a, **k):
        super (OnFloorEntity, self).__init__ (*a, **k)
        self.enable_collision ()
        self.on_collide += self.on_standing_collide
        self._is_on_floor = False
        self.is_on_floor_timer = 0.
        self.on_is_on_floor_change = Signal ()
        
    @property
    def is_on_floor (self):
        return self._is_on_floor

    def do_update (self, timer):
        self.is_on_floor_timer -= timer.delta
        if self.is_on_floor_timer < 0.0:
            self.is_on_floor_timer = 0.0
            self._is_on_floor = False
            self.on_is_on_floor_change (self, False)
        super (OnFloorEntity, self).do_update (timer)

    @weak_slot
    def on_standing_collide (self, ev, me, other):
        pos = ev.getContactPoint (0)
        if pos.getZ () < self.position.getZ ():
            self._is_on_floor = True
            self.on_is_on_floor_change (self, True)
            self.is_on_floor_timer = self.on_floor_delay


class DelegateOnFloorEntity (DelegateEntity):
    
    @property
    def is_on_floor (self):
        return self.delegate.is_on_floor

    def _set_is_on_floor_timer (self, is_on_floor_timer):
        self.delegate.is_on_floor_timer = is_on_floor_timer

    def _get_is_on_floor_timer (self):
        return self.delegate.is_on_floor_timer

    is_on_floor_timer = property (_get_is_on_floor_timer,
                                  _set_is_on_floor_timer)
