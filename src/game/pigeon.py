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

from base.signal import weak_slot

from ent.observer import ObservableSpatialEntity
from ent.panda import ModelEntity
from ent.physical import (StandingPhysicalEntityDecorator,
                          DynamicPhysicalEntity)

from core.state import StateManager, State
from core.util import *
from core import task

import phys.geom as geom
import phys.mass as mass

from flock import BoidParams, BoidEntity, FlockEntity
from kill import KillableEntity
from crawler import CrawlerEntityDecorator

import random
import weakref
from pandac.PandaModules import Vec3

class Pigeon (BoidEntity,
              ModelEntity,
              KillableEntity,
              StateManager):

    MODEL = 'char/pigeon-anims.egg'
    ANIMS = { 'walk'    : 'char/pigeon-walk.egg',
              'fly'     : 'char/pigeon-fly.egg',
              'takeoff' : 'char/pigeon-takeoff.egg',
              'land'    : 'char/pigeon-land.egg',
              'idle'    : 'char/pigeon-idle.egg' }
    
    def __init__ (self,
                  model = MODEL,
                  the_boy = None,
                  *a, **k):
        super (Pigeon, self).__init__ (
            geometry = geom.capsule (2, 1),
            mass     = mass.sphere (1, 2),
            model    = model,
            *a, **k)

        self.on_death += self.on_pigeon_death

        self.physical_hpr = Vec3 (90, 0, 0)
        self.the_boy = the_boy
        self.params = BoidParams ()
        
        # Fix model coordinates
        self.model_position = Vec3 (0, 0, -2)
        self.model_scale    = Vec3 (0.08, 0.08, 0.08)
        self.model_hpr      = Vec3 (180, 0, 0)
        # self.model.setTexture (loader.loadTexture ('obj/black.png'))
        
        # Sounds
        self.die_sounds = map (self.load_sound,
                               [ 'snd/electrocute-medium.wav',
                                 'snd/electrocute-short.wav' ])

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

    @weak_slot
    def on_pigeon_death (self):
        self.force_finish ()
        self.disable_physics ()
        random.choice (self.die_sounds).play ()


class PatrolState (State):

    min_wait = 5
    max_wait = 10

    def do_setup (self):
        return None
        self.tasks.add (task.sequence (
            task.wait (random.uniform (self.min_wait,
                                       self.max_wait)),
            lambda: self.manager.change_state ('walk')))

class FollowState (State):
    
    def do_update (self, timer):
        super (FollowState, self).do_update (timer)
        self.manager.params.boid_target = self.manager.the_boy.position        

class FearState (State): pass
class WalkState (State): pass
class FoodState (State): pass

"""
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
"""

"""
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
"""
