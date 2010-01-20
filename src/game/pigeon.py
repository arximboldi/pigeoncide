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

from ent.observer import ObservableSpatialEntity
from ent.panda import ModelEntity
from ent.physical import (StandingPhysicalEntityDecorator,
                          DynamicPhysicalEntity)

from core.state import StateManager, State
from core.util import *
from core import task

import phys.geom as geom
import phys.mass as mass

from flock import BoidEntityDecorator, Flock
from kill import KillableEntity
from crawler import CrawlerEntityDecorator

import random
import weakref
from pandac.PandaModules import Vec3

class PigeonBoid (BoidEntityDecorator):
    patrol_dist = 100
    patrol_dist_sq = patrol_dist ** 2
    
class PigeonFlock (Flock):        

    def do_update (self, timer):
        super (PigeonFlock, self).do_update (timer)

        if all (map (self.reached_target, self.boids)):
            (minx, miny, minz), (maxx, maxy, maxz) = self.flock_bounds 
            new_target = Vec3 (random.uniform (minx, maxx),
                               random.uniform (miny, maxy),
                               random.uniform (minz, maxz))
            for x in self.boids:
                x.boid_target = new_target

    def reached_target (self, pigeon):
        return (
            not pigeon.boid_target or
            (pigeon.boid_target - pigeon.position).lengthSquared () <
            pigeon.patrol_dist_sq)


class Pigeon (ModelEntity,
              KillableEntity,
              DynamicPhysicalEntity,
              StateManager):

    MODEL = '../data/mesh/pigeon-old.x'
    ANIMS = {}
    
    def __init__ (self,
                  flock = None,
                  model = MODEL,
                  the_boy = None,
                  *a, **k):
        k ['entities'] = flock.entities
        super (Pigeon, self).__init__ (
            geometry = geom.capsule (2, 1),
            mass     = mass.sphere (1, 2),
            model    = model,
            *a, **k)

        self.physical_hpr = Vec3 (90, 0, 0)
        
        self._flock  = weakref.ref (flock)
        self.the_boy = the_boy

        # Fix model coordinates
        self.model_position = Vec3 (0, 0, -2)
        self.model_scale    = Vec3 (0.05, 0.05, 0.05)
        self.model_hpr      = Vec3 (180, 0, 0)

        self.die_sounds = map (self.load_sound,
                               [ 'snd/electrocute_medium.wav',
                                 'snd/electrocute_short.wav' ])

        # Setup AI state machine
        self.add_state ('patrol', PatrolState)
        self.add_state ('walk',   WalkState)
        self.add_state ('follow', FollowState)
        self.add_state ('fear',   FearState)
        self.add_state ('food',   FoodState)

        self.start ('follow')

    def do_update (self, timer):
        """
        Hack to avoid the tunneling effect. We manually sweep the
        collision sphere using a cylinder.
        """
        super (Pigeon, self).do_update (timer)
        vlen = self.linear_velocity.length ()
        self.geom.setParams (2., vlen * timer.delta)

    @property
    def flock (self):
        return self._flock ()
        
    def on_die (self):
        self.force_finish ()
        self.disable_physics ()
        random.choice (self.die_sounds).play ()


class FlockingState (State):

    def __init__ (self, *a, **k):
        super (FlockingState, self).__init__ (*a, **k)
        self.boid = PigeonBoid (flock    = self.manager.flock,
                                delegate = self.manager)
        
    def do_release (self):
        self.boid.dispose ()

class CrawlingState (State):

    def __init__ (self, *a, **k):
        super (CrawlingState, self).__init__ (*a, **k)
        self.crawler = CrawlerEntityDecorator (self.manager)
        print self.manager.hpr
        self.crawler.angle = to_rad (self.manager.hpr.getX ())
        
    def do_release (self):
        self.crawler.dispose ()

class PatrolState (FlockingState):

    min_wait = 5
    max_wait = 10

    def do_setup (self):
        return None
        self.tasks.add (task.sequence (
            task.wait (random.uniform (self.min_wait,
                                       self.max_wait)),
            lambda: self.manager.change_state ('walk')))

class FollowState (FlockingState):
    
    def do_update (self, timer):
        super (FollowState, self).do_update (timer)
        self.boid.boid_target = self.manager.the_boy.position        


class FearState (FlockingState): pass

class WalkState (CrawlingState): pass

class FoodState (CrawlingState): pass

