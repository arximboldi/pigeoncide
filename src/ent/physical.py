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

from entity import Entity, DelegateEntity, EntityManager
from task import TaskEntity

from pandac.PandaModules import *
import math

from phys.physics import Physics
import phys.mass as mass
import phys.geom as geom


class PhysicalEntityManager (EntityManager):

    def __init__ (self, physics = None, *a, **k):
        super (PhysicalEntityManager, self).__init__ (*a, **k)
        if physics:
            self.physics = physics
        else:
            self.physics = Physics ()
            
        self.tasks.add (self.physics)


class StaticPhysicalEntity (Entity):

    def __init__ (self,
                  entities = None,
                  geometry = geom.box (1, 1, 1),
                  *a, **k):
        super (StaticPhysicalEntity, self).__init__ (
            entities = entities,
            *a, **k)
        self._geom = geometry (entities.physics.space)

    def set_position (self, pos):
        super (StaticPhysicalEntity, self).set_position (pos)
        self._geom.setPosition (pos)
            
    def set_hpr (self, hpr):
        super (StaticPhysicalEntity, self).set_hpr (hpr)
        q = Quat ()
        q.setHpr (hpr) # FIXME: slow
        self._geom.setQuaternion (q)

    def set_scale (self, scale):
        super (StaticPhysicalEntity, self).set_scale (scale)
        # FIXME: self._geom.setScale (scale)


class DynamicPhysicalEntity (TaskEntity):

    def __init__ (self,
                  entities = None,
                  geometry = geom.box (1, 1, 1),
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

        self._geom = geometry (physics.space)
        self._geom.setBody (self._body)
        
        self._updating = False

    @property
    def mass (self):
        return self._mass.getMagnitude ()

    @property
    def body (self):
        return self._body

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
            self._body.setPosition (pos)
            
    def set_hpr (self, hpr):
        super (DynamicPhysicalEntity, self).set_hpr (hpr)
        q = Quat ()
        q.setHpr (hpr) # FIXME: slow
        if not self._updating:
            self._body.setQuaternion (q)

    def set_scale (self, scale):
        super (DynamicPhysicalEntity, self).set_scale (scale)
        # FIXME if not self._updating:
        # self._body.setScale (scale)
        
    def update (self, timer):
        super (DynamicPhysicalEntity, self).update (timer)

        pos = self._body.getPosition ()
        hpr = self._body.getQuaternion ()
        q = Quat ()
        q.setX (hpr.getX ())
        q.setY (hpr.getY ())
        q.setZ (hpr.getZ ())
        q.setW (hpr.getW ())
        hpr = q.getHpr () # FIXME: Slow!
        
        self._updating = True
        self.set_position (pos)        
        self.set_hpr (hpr)
        self._updating = False

    linear_velocity = property (get_linear_velocity, set_linear_velocity)
    angular_velocity = property (get_angular_velocity, set_angular_velocity)


class DelegateDynamicPhysicalEntity (DelegateEntity):

    @property
    def body (self):
        return self.delegate.body

    @property
    def speed (self):
        return self.delegate.speed
    
    def add_force (self, force):
        self.delegate.add_force (force)

    def add_torque (self, force):
        self.delegate.add_torque (torque)

    def set_force (self, force):
        self.delegate.set_force (force)

    def set_torque (self, force):
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


class StandingPhysicalEntity (DynamicPhysicalEntity):

    def __init__ (self, *a, **k):
        super (StandingPhysicalEntity, self).__init__ (*a, **k)
        self.angle = 0

    def update (self, timer):
        hpr = self._body.getQuaternion ()

        # http://www.euclideanspace.com/maths/geometry/rotations/
        # conversions/angleToQuaternion/index.htm      
        self._body.setQuaternion (Quat (math.sin (self.angle / 2), 0, 0,
                                        math.cos (self.angle / 2)))
        self._body.setTorque (0, 0, 0)
        self._body.setAngularVel (0, 0, 0)

        super (StandingPhysicalEntity, self).update (timer)


class DelegateStandingPhysicalEntity (DelegateDynamicPhysicalEntity):

    def _set_angle (self, angle):
        self.delegate.angle = angle

    def _get_angle (self):
        return self.delegate.angle

    angle = property (_get_angle, _set_angle)

