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

This older version uses a velocity-based implementation of the
flocking algorithm. It is outdated because it caused the animation to
be to jerky and the movements, specially the rotations, to be too fast
--maybe apropiate for fish, but not for birds. Also it was hard to
implement the walking behaviour using this, which lead to the
implementation of entity decorators to be able to dynamically switch
between a CrawlerEntity and a BoidEntity to control a Pigeon..
"""

from direct.directtools.DirectGeometry import LineNodePath
from pandac.PandaModules import *

from ent.entity import Entity
from ent.task import TaskEntity
from ent.physical import (DynamicPhysicalEntity,
                          DelegateDynamicPhysicalEntity)

from base.util import nop
import random
import weakref
import math

class Flock (TaskEntity):

    flock_bounds = ((-300, -300, 0), (300, 300, 200))

    def __init__ (self, *a, **k):
        super (Flock, self).__init__(*a, **k)
        self.boids = []
        self.leader = None
        self.boids_cache = []
        
    def choose_leader (self):
        self.leader = self.boids [random.randint (0, len (self.boids) - 1)]

    def remove (self, boid):
        self.boids.remove (boid)

    def dispose (self):
        super (FlockEntity, self).dispose ()
        for x in self.boids:
            x.dispose ()

    def add_boid (self, boid):
        self.boids.append (boid)
        if len (self.boids) == 1:
            self.leader = boid

    def do_update (self, timer):
        self.boids_cache = \
            [ (x, x.position, x.linear_velocity) for x in self.boids ]


class BoidEntityBase (TaskEntity):

    boid_power        = 10
    
    boid_f_cohesion   = 0.01
    boid_f_avoidance  = 1
    boid_f_alignment  = 0.125
    boid_f_bounds     = 10
    boid_f_randomness = 0
    boid_f_flight     = 0
    boid_f_target     = 0.01

    boid_speed        = 100
    boid_speed_sq     = boid_speed * boid_speed
    boid_max_far      = 1000
    boid_max_far_sq   = boid_max_far * boid_max_far

    boid_mindist      = 5
    boid_mindist_sq   = boid_mindist * boid_mindist 
    boid_maxdist      = 20
    boid_maxdist_sq   = boid_maxdist * boid_maxdist

    boid_height       = 50.0
    
    boid_target       = None
    
    def __init__ (self, flock = None, *a, **k):
        super (BoidEntityBase, self).__init__ (*a, **k)
        self.flock = weakref.proxy (flock)
        self.flock.add_boid (self)

        self._debug_line = LineNodePath (self.entities.render,
                                         'caca', 2, Vec4 (1, 0, 0, 0))

    def dispose (self):
        self.flock.remove (self)
        super (BoidEntityBase, self).dispose ()
        
    def do_update (self, timer):
        super (BoidEntityBase, self).do_update (timer)
        self.update_flocking (timer)

    def update_flocking (self, timer):
        self._curr_position = self.position
        self._curr_velocity = self.linear_velocity
        
        self.neighbours = self.find_neighbours ()

        cohesion   = self.rule_cohesion ()
        avoidance  = self.rule_avoidance ()
        alignment  = self.rule_alignment ()
        bounds     = self.rule_bounds ()
        flight     = self.rule_flight ()
        randomness = self.rule_randomness ()
        target     = self.rule_target ()
        
        v = (cohesion   * self.boid_f_cohesion   +
             avoidance  * self.boid_f_avoidance  +
             alignment  * self.boid_f_alignment  +
             bounds     * self.boid_f_bounds     +
             flight     * self.boid_f_flight     +
             randomness * self.boid_f_randomness +
             target     * self.boid_f_target) \
             * self.boid_power
        
        if v.lengthSquared () > self.boid_speed_sq:
            v.normalize ()
            v *= self.boid_speed
        
        self.linear_velocity  = v
        self.angular_velocity = Vec3 (0, 0, 0)    
        self.set_torque (Vec3 (0, 0, 0))
        self.set_force  (Vec3 (0, 0, 0))

        v.normalize ()
        self.hpr = Vec3 (- math.atan2 (v.getX (), v.getY ())
                         * 180. / math.pi, 
                         math.asin (v.getZ ())
                         * 180. / math.pi, 0)
        
        # self._debug_line.reset ()
        # self._debug_line.setColor (Vec4 (1, 0, 0, 0))
        # self._debug_line.drawLines (
        #     [[self.position, self.position + v * vlen * timer.delta]])
        # self._debug_line.create ()
            
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
        mypos = self._curr_position
        return [ (x, p, v)
                 for (x, p, v)
                 in self.flock.boids_cache
                 if (mypos - p).lengthSquared () < self.boid_maxdist_sq
                 and x != self ]

    def rule_avoidance (self):
        avoid = Vec3 ()
        mypos = self._curr_position
        for (x, p, v) in self.neighbours:
            distsq = (p - mypos).lengthSquared ()
            if distsq < self.boid_mindist_sq:
                avoid -= p - mypos
        return avoid
    
    def rule_cohesion (self):
        center = Vec3 (0, 0, 0)
        if self.neighbours:
            for (x, p, v) in self.neighbours:
                center += p
            center /= len (self.neighbours)
        cohesion = (center - self._curr_position) / 100.
        
        return cohesion
    
    def rule_bounds (self):
        bounds = Vec3 (0, 0, 0)
        if self._curr_position.lengthSquared () > self.boid_max_far_sq:
            bounds = bounds - self._curr_position
            bounds.normalize ()
        return bounds

    def rule_alignment (self):
        velocity = Vec3 (0, 0, 0)
        if self.neighbours:
            for (x, p, v) in self.neighbours:
                velocity += v
            velocity /= len (self.neighbours)
        return velocity

    def rule_flight (self):
        if self._curr_position.getZ () < self.boid_height:
            return Vec3 (0, 0, 1.0)
        return Vec3 (0, 0, 0)

    def rule_randomness (self):
        if self._curr_velocity.lengthSquared () < self.boid_speed_sq:
            return Vec3 (random.random (),
                         random.random (),
                         0)
        return Vec3 (0, 0, 0)

    def rule_target (self):
        factor = 10.
        if self.neighbours:
            factor = 1.
        if self.boid_target:
            return (self.boid_target - self._curr_position) * factor
        return Vec3 ()


class BoidEntity (BoidEntityBase,
                  DynamicPhysicalEntity):
    pass


class BoidEntityDecorator (
    DelegateDynamicPhysicalEntity,
    BoidEntityBase):
    pass


def make_random_flock (entities,
                       num_boids,
                       bounds    = Flock.flock_bounds,
                       flock_cls = Flock,
                       boid_cls  = BoidEntity):

    flock = flock_cls (entities = entities)
    (minx, miny, minz), (maxx, maxy, maxz) = bounds

    for i in xrange (num_boids):
        b = boid_cls (flock = flock)
        b.position = Vec3 (random.uniform (minx, maxx),
                           random.uniform (miny, maxy),
                           random.uniform (minz, maxz))
    flock.choose_leader ()
    flock.flock_bounds = bounds
    
    return flock
