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

from pandac.PandaModules import Vec3

from core.task import Task
from ent.physical import (DynamicPhysicalEntity,
                          DelegateDynamicPhysicalEntity)

import random
import weakref

class Flock (TaskEntity):

    bird_cohesion   = .1 / 5.
    bird_avoidance  = .1 / 5.
    bird_alignment  = .1 / 5.
    bird_randomness = .1 / 5.
    bird_flight     = .1 / 5.
    
    bird_angle      = 45.0
    bird_distance   = 100.0

    def __init__ (self,
                  *a, **k):
        super (self, *a, **k).__init__ (*a, **k)
        self.birds = []
        self.leader = None

    def choose_leader (self):
        self.leader = self.birds [random.randint (0, len (self.birds) - 1)]

    def remove (self, bird):
        bird.dispose ()
        self.birds.remove (bird)

    def _add_bird (self, bird):
        self.birds += bird
        if len (self.birds) == 1:
            self.leader = bird

    def dispose (self):
        super (FlockEntity)


class BirdBase (TaskEntity):

    flight_height = 100.0
    
    def __init__ (self, flock = None, *a, **k):
        super (BirdEntityBase, self).__init__ (
            entities = k.get ('entities', flock.entities),
            *a, **k)
        self.flock = weakref.proxy (flock)
        self.flock._add_bird (flock)

    def update (self, timer):
        self.neighbours = self.find_neighbours ()

        cohesion   = self.get_cohesion ()
        avoidance  = self.get_avoidance ()
        alignment  = self.get_alignment ()
        flight     = self.get_flight ()
        randomness = self.get_randomness ()

        force = self.flock.bird_cohesion   * cohesion   + \
                self.flock.bird_avoidance  * avoidance  + \
                self.flock.bird_alignment  * alignment  + \
                self.flock.bird_randomness * randomness + \
                self.flock.bird_flight     * flight

        self.add_force (force)

    def find_neighbours (self):
        return filter (
            lambda x: ((self.position - x.position).lengthSquared ()
                       < self.flock.bird_distance),
            self.flock.birds)

    def get_cohesion (self):
        center = Vec3 (0, 0, 0)
        if self.neighbours:
            for x in self.neighbours:
                center += x.position
            center /= len (self.neighbours)
        cohesion = self.center - self.position
        cohesion.normalize ()
        return cohesion
    
    def get_avoidance (self):
        return Vec3 (0, 0, 0)

    def get_alignment (self):
        velocity = Vec3 (0, 0, 0)
        if self.neighbours:
            for x in self.neighbours:
                vel = x.linear_velocity
                vel.normalize ()
                velocity += vel
            velocity /= len (self.neighbours)
            velocity.normalize ()
        return velocity

    def get_flight (self):
        if self.position.getZ () < self.flight_hight:
            return Vec3 (0, 0, 1.0f)
        return Vec3 (0, 0, 0)

    def get_randomness (self):
        return Vec3 (random.random (),
                     random.random (),
                     random.random ())


class Bird (DynamicPhysicalEntity, BirdBase):
    pass


class DelegateBird (DelegateDynamicPhysicalEntity, BirdBase):
    pass


def make_random_flock (entities,
                       num_birds,
                       center,
                       size,
                       bird_cls = Bird):

    flock = Flock (entities = entities)
    for i in xrange (num_birds):
        b = bird_cls (flock = flock)
        b.position = Vec3 (random.uniform (center.getX () - size/2, size),
                           random.uniform (center.getY () - size/2, size),
                           random.uniform (center.getZ () - size/2, size))
    flock.choose_leader ()
