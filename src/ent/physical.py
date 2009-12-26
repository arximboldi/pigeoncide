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

from entity import Entity
from pandac.PandaModules import *
import math
import phys.mass as mass

class StaticPhysicalEntity (Entity):

    def __init__ (self,
                  physics = None,
                  geometry = None,
                  *a, **k):
        
        super (StaticPhysicalEntity, self).__init__ (*a, **k)
        self._geom = geometry (physics.space)

    def set_position (self, pos):
        super (StaticPhysicalEntity, self).set_position (pos)
        self._geom.setPosition (*pos)
            
    def set_hpr (self, hpr):
        super (StaticPhysicalEntity, self).set_hpr (hpr)
        q = Quat ()
        q.setHpr (hpr) # FIXME: slow
        self._geom.setQuaternion (q)

    def set_scale (self, scale):
        super (StaticPhysicalEntity, self).set_scale (scale)
        self._geom.setScale (*scale)

class DynamicPhysicalEntity (Entity):

    def __init__ (self,
                  physics  = None,
                  geometry = None,
                  mass     = mass.box (1000, 1, 1, 1),
                  *a, **k):
        super (DynamicPhysicalEntity, self).__init__ (*a, **k)
        
        self._mass = OdeMass ()
        mass (self._mass)
        
        self._body = OdeBody (physics.world)
        self._body.setMass (self._mass)

        self._geom = geometry (physics.space)
        self._geom.setBody (self._body)
        
        self._updating = False

    @property
    def speed (self):
        vel = self._body.getLinearVel ()
        return (vel.getX (), vel.getY (), vel.getZ ())
        
    def set_position (self, pos):
        super (DynamicPhysicalEntity, self).set_position (pos)
        if not self._updating:
            self._body.setPosition (*pos)
            
    def set_hpr (self, hpr):
        super (DynamicPhysicalEntity, self).set_hpr (hpr)
        q = Quat ()
        q.setHpr (hpr) # FIXME: slow
        if not self._updating:
            self._body.setQuaternion (q)

    def set_scale (self, scale):
        super (DynamicPhysicalEntity, self).set_scale (scale)
        if not self._updating:
            self._body.setScale (*scale)

    def apply_force (self, force):
        self._body.addForce (*force)
            
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
        self.set_position ((pos.getX (), pos.getY (), pos.getZ ()))        
        self.set_hpr ((hpr.getX (), hpr.getY (), hpr.getZ ()))
        self._updating = False

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
