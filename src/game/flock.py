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
Modified version of the popular flocking algorithm by Craig Reynolds,
which is described in the Algorythms for Computer Games in Turku
University.

Interesting links about it:
  * http://www.red3d.com/cwr/boids/
  * http://www.kfish.org/boids/pseudocode.html
"""

from pandac.PandaModules import Vec3

from ent.entity import Entity
from ent.task import TaskEntity
from ent.physical import (DynamicPhysicalEntity,
                          DelegateDynamicPhysicalEntity)

import random
import weakref
import math

class Flock (TaskEntity):

    boid_power      = 10
    
    boid_cohesion   = 0.01
    boid_avoidance  = 1
    boid_alignment  = 0.125
    boid_bounds     = 10
    boid_randomness = 1
    boid_flight     = 0
    boid_target     = 0.01

    boid_speed      = 100
    boid_speed_sq   = boid_speed * boid_speed
    boid_max_far    = 500
    boid_max_far_sq = boid_max_far * boid_max_far

    boid_mindist    = 5
    boid_mindist_sq = boid_mindist * boid_mindist 
    boid_maxdist    = 20
    boid_maxdist_sq = boid_maxdist * boid_maxdist

    boid_height     = 50.0
    
    target          = None
    
    def __init__ (self, *a, **k):
        super (Flock, self).__init__(*a, **k)
        self.boids = []
        self.leader = None

    def choose_leader (self):
        self.leader = self.boids [random.randint (0, len (self.boids) - 1)]

    def remove (self, boid):
        boid.dispose ()
        self.boids.remove (boid)

    def dispose (self):
        super (FlockEntity, self).dispose ()
        for x in self.boids:
            x.dispose ()

    def _add_boid (self, boid):
        self.boids.append (boid)
        if len (self.boids) == 1:
            self.leader = boid


class BoidBase (TaskEntity):
    
    def __init__ (self, flock = None, *a, **k):
        k ['entities'] = flock.entities
        super (BoidBase, self).__init__ (*a, **k)
        self.flock = weakref.proxy (flock)
        self.flock._add_boid (self)

    def update (self, timer):
        super (BoidBase, self).update (timer)
        
        self.neighbours = self.find_neighbours ()

        cohesion   = self.rule_cohesion ()
        avoidance  = self.rule_avoidance ()
        alignment  = self.rule_alignment ()
        bounds     = self.rule_bounds ()
        flight     = self.rule_flight ()
        randomness = self.rule_randomness ()
        target     = self.rule_target ()
        
        v = (cohesion   * self.flock.boid_cohesion   +
             avoidance  * self.flock.boid_avoidance  +
             alignment  * self.flock.boid_alignment  +
             bounds     * self.flock.boid_bounds     +
             flight     * self.flock.boid_flight     +
             randomness * self.flock.boid_randomness +
             target     * self.flock.boid_target) \
             * self.flock.boid_power

        
        if v.lengthSquared () > self.flock.boid_speed_sq:
            v.normalize ()
            v *= self.flock.boid_speed
        
        self.linear_velocity  = v
        self.angular_velocity = Vec3 (0, 0, 0)

        v.normalize ()
        self.hpr              = Vec3 (- math.atan2 (v.getX (), v.getY ())
                                      * 180. / math.pi, 
                                      math.asin (v.getZ ())
                                      * 180. / math.pi, 0)
        
        self.set_torque (Vec3 (0, 0, 0))
        self.set_force  (Vec3 (0, 0, 0))


        # HACK: Try to avoid the fucking tunneling
        # http://www.ode.org/old_list_archives/2003-July/009477.html
        # physics = self.entities.physics.world
        # ray = OdeRayGeom (100000.0)
        # ray.set (self.position, v)

        # collision = physics.collide_world (ray)

        # cgeom   = OdeContactGeom ()
        # cgeom.setG1 (target)
        # cgeom.setG2 (self._geom)
        # cgeom.setDepth (HITDISTANCE)
        # cgeom.setPos (POSITION)
        
        # contact = OdeContact ()
        # contact.setContactGeom (cgeom)
        # contact.setSurface (OdeSurfaceParameters (FRICTIONLESS))
        # joint   = OdeContactJoint (self.entities.physics.world,
        #                            contact)

    def find_neighbours (self):
        return filter (
            lambda x: ((self.position - x.position).lengthSquared ()
                       < self.flock.boid_maxdist_sq) and x != self,
            self.flock.boids)

    def rule_avoidance (self):
        avoid = Vec3 ()
        for x in self.neighbours:
            distsq = (x.position - self.position).lengthSquared ()
            if distsq < self.flock.boid_mindist_sq:
                avoid -= x.position - self.position
        return avoid
    
    def rule_cohesion (self):
        center = Vec3 (0, 0, 0)
        if self.neighbours:
            for x in self.neighbours:
                center += x.position
            center /= len (self.neighbours)
        cohesion = (center - self.position) / 100.
        
        return cohesion
    
    def rule_bounds (self):
        bounds = Vec3 (0, 0, 0)
        if self.position.lengthSquared () > self.flock.boid_max_far_sq:
            bounds = bounds - self.position
            bounds.normalize ()
        return bounds

    def rule_alignment (self):
        velocity = Vec3 (0, 0, 0)
        if self.neighbours:
            for x in self.neighbours:
                velocity += x.linear_velocity
            velocity /= len (self.neighbours)
        return velocity

    def rule_flight (self):
        if self.position.getZ () < self.flock.boid_height:
            return Vec3 (0, 0, 1.0)
        return Vec3 (0, 0, 0)

    def rule_randomness (self):
        if self.linear_velocity.lengthSquared () < self.flock.boid_speed_sq:
            return Vec3 (random.random (),
                         random.random (),
                         0)
        return Vec3 (0, 0, 0)

    def rule_target (self):
        if self.flock.target:
            return Vec3 (*self.flock.target.position) - self.position
        return Vec3 ()


class Boid (BoidBase, DynamicPhysicalEntity):
    pass


class DelegateBoid (DelegateDynamicPhysicalEntity, BoidBase):
    pass


def make_random_flock (entities,
                       num_boids,
                       center,
                       size,
                       boid_cls = Boid):

    flock = Flock (entities = entities)
    for i in xrange (num_boids):
        b = boid_cls (flock = flock)
        b.position = Vec3 (random.uniform (center.getX () - size/2, size),
                           random.uniform (center.getY () - size/2, size),
                           random.uniform (center.getZ () - size/2, size))
    flock.choose_leader ()
    return flock
