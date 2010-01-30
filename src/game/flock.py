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

This version uses forces to model the behaviour. This allows softer
movements, more realistic animation for birds and can model the full
behaviour of the pigeons --both walking and flying-- with a single
behavioural model. This is a lot of help, and makes useless the
relatively complex but neat Decorator system that we made for the
entities in order to model easily the whole Pigeon AI using state
machines..
"""

from direct.directtools.DirectGeometry import LineNodePath
from pandac.PandaModules import *

from ent.entity import Entity
from ent.task import TaskEntity
from ent.physical import (DynamicPhysicalEntity,
                          DelegateDynamicPhysicalEntity)

from base.util import nop
from core.util import *

import random
import weakref
import math

class FlockEntity (TaskEntity):

    flock_bounds = ((-300, -300, 0), (300, 300, 200))

    def __init__ (self, *a, **k):
        super (FlockEntity, self).__init__(*a, **k)
        self.boids = []
        self.leader = None
        self.boids_cache = []
        
    def choose_leader (self):
        self.leader = self.boids [random.randint (0, len (self.boids) - 1)]

    def remove (self, boid):
        try:
            self.boids.remove (boid)
        except ValueError, e:
            pass
        
    def dispose (self):
        super (FlockEntity, self).dispose ()
        
    def add_boid (self, boid):
        self.boids.append (boid)
        boid.flock = weakref.proxy (self)
        if len (self.boids) > 0:
            self.leader = boid

    def del_boid (self, boid):
        self.boids.remove (boid)
        if len (self.boids) > 0:
            self.leader = boid

    def do_update (self, timer):
        self.boids_cache = \
            [ (x, x.position, x.linear_velocity) for x in self.boids ]


class BoidParams (object):

    # All rules effect
    boid_power        = 1000
    boid_flying       = True
    boid_flocking     = True

    # Individual rule effect
    boid_f_cohesion   = 0.01
    boid_f_collision  = 0.01
    boid_f_avoidance  = 0.1
    boid_f_alignment  = 1
    boid_f_bounds     = 0.001
    boid_f_randomness = .2
    boid_f_flight     = 0
    boid_f_target     = 0.001

    # Constraints
    boid_speed        = 150
    boid_max_far      = 600
    boid_mindist      = 5
    boid_maxdist      = 20
    boid_height       = 50.0    
    boid_target       = None


class BoidEntityBase (TaskEntity):

    params = BoidParams
    
    def __init__ (self, flock = None, *a, **k):
        k ['entities'] = flock.entities
        super (BoidEntityBase, self).__init__ (*a, **k)
        self.flock = weakref.proxy (flock)
        self.flock.add_boid (self)

        self._debug_line = LineNodePath (self.entities.render,
                                         'caca', 2, Vec4 (1, 0, 0, 0))

        self.change_params (self.params)

    def change_params (self, params):
        if params.boid_flocking and not self.params.boid_flocking:
            self.flock.add_boid (self)
        elif not params.boid_flocking and self.params.boid_flocking:
            self.flock.del_boid (self)
        self.body.setGravityMode (not params.boid_flying)
        self.params = params
    
    def dispose (self):
        self.flock.remove (self)
        super (BoidEntityBase, self).dispose ()
        
    def do_update (self, timer):
        super (BoidEntityBase, self).do_update (timer)
        if self.params.boid_flocking:
            self.update_flocking (timer)

    def update_flocking (self, timer):
        self._curr_position = self.position
        self._curr_velocity = self.linear_velocity
        linvel              = self.linear_velocity
        
        self.neighbours = self.find_neighbours ()

        cohesion   = self.rule_cohesion ()
        avoidance  = self.rule_avoidance ()
        alignment  = self.rule_alignment ()
        bounds     = self.rule_bounds ()
        flight     = self.rule_flight ()
        randomness = self.rule_randomness ()
        target     = self.rule_target ()
        
        f = (cohesion   * self.params.boid_f_cohesion   +
             avoidance  * self.params.boid_f_avoidance  +
             alignment  * self.params.boid_f_alignment  +
             bounds     * self.params.boid_f_bounds     +
             flight     * self.params.boid_f_flight     +
             randomness * self.params.boid_f_randomness +
             target     * self.params.boid_f_target) \
             * self.params.boid_power

        linvel += f * timer.delta
        if linvel.lengthSquared () > self.params.boid_speed ** 2:
            linvel = normalized (linvel) * self.params.boid_speed

        self.linear_velocity = linvel

        linvel.normalize ()
        self.hpr = Vec3 (- math.atan2 (linvel.getX (), linvel.getY ())
                         * 180. / math.pi, 
                         math.asin (linvel.getZ ())
                         * 180. / math.pi, 0)

    def find_neighbours (self):
        mypos = self._curr_position
        return [ (x, p, v)
                 for (x, p, v)
                 in self.flock.boids_cache
                 if (mypos - p).lengthSquared () < self.params.boid_maxdist ** 2
                 and x != self ]

    def rule_avoidance (self):
        avoid = Vec3 ()
        mypos = self._curr_position
        for (x, p, v) in self.neighbours:
            distsq = (p - mypos).lengthSquared ()
            if distsq < self.params.boid_mindist ** 2:
                avoid -= p - mypos
        return avoid

    def rule_collision (self, timer):
        res = Vec3 (0, 0, 0)
        physics = self.entities.physics
        ray = OdeRayGeom (1000000.0)
        ray.set (self._curr_position + self._curr_velocity * timer.delta + 1,
                 self._curr_velocity)
        col = physics.collide_world (ray)
        if col and not col.isEmpty ():
            res = self._curr_position - col.getContactPoint (0)
        return res
    
    def rule_cohesion (self):
        center = Vec3 (0, 0, 0)
        if self.neighbours:
            for (x, p, v) in self.neighbours:
                center += p
            center /= len (self.neighbours)
        cohesion = center - self._curr_position
        
        return cohesion
    
    def rule_bounds (self):
        bounds = Vec3 (0, 0, 0)
        if self._curr_position.lengthSquared () > self.params.boid_max_far ** 2:
            bounds = bounds - self._curr_position
        if self._curr_position.getZ () < 20:
            bounds += Vec3 (0, 0, 20 - self._curr_position.getZ ())
        return bounds

    def rule_alignment (self):
        velocity = Vec3 (0, 0, 0)
        if self.neighbours:
            for (x, p, v) in self.neighbours:
                velocity += v
            velocity /= len (self.neighbours)
        return normalized (velocity)

    def rule_flight (self):
        if self._curr_position.getZ () < self.params.boid_height:
            return Vec3 (0, 0, 1.0)
        return Vec3 (0, 0, 0)

    def rule_randomness (self):
        if self._curr_velocity.lengthSquared () < self.params.boid_speed ** 2:
            return Vec3 (random.random (),
                         random.random (),
                         0)
        return Vec3 (0, 0, 0)

    def rule_target (self):
        factor = 10.
        if self.neighbours:
            factor = 1.
        if self.params.boid_target:
            return (self.params.boid_target - self._curr_position) * factor
        return Vec3 ()


class BoidEntity (BoidEntityBase,
                  DynamicPhysicalEntity):
    pass


class BoidEntityDecorator (
    BoidEntityBase,
    DelegateDynamicPhysicalEntity):
    pass


def make_random_flock (entities,
                       num_boids,
                       bounds    = FlockEntity.flock_bounds,
                       boid_cls  = BoidEntity,
                       flock_cls = FlockEntity):

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
