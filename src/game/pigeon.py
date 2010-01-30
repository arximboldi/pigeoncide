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
from base.util import nop

from ent.observer import ObservableSpatialEntity
from ent.panda import ActorEntity
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
from weapon import Hittable
from physics import pigeon_category

import random
import weakref
from pandac.PandaModules import Vec3


class Pigeon (BoidEntity,
              ActorEntity,
              KillableEntity,
              StateManager,
              Hittable):
    """
    TODO: Actually a StateManager has too much innecesary overhead. We
    could try to make a lightweight version of it for this kind of
    use.
    """
    
    pigeon_model = 'char/pigeon-anims.egg'
    pigeon_anims = { 'walk'    : 'char/pigeon-walk.egg',
                     'fly'     : 'char/pigeon-fly.egg',
                     'takeoff' : 'char/pigeon-takeoff.egg',
                     'land'    : 'char/pigeon-land.egg',
                     'idle'    : 'char/pigeon-idle.egg' }

    pigeon_death_sounds = [ 'snd/electrocute-medium.wav',
                            'snd/electrocute-short.wav' ]
    
    def __init__ (self,
                  model = pigeon_model,
                  anims = pigeon_anims,
                  boys  = [],
                  *a, **k):
        super (Pigeon, self).__init__ (
            geometry = geom.capsule (2, 1),
            mass     = mass.sphere (1, 2),
            model    = model,
            anims    = anims,
            category = pigeon_category,
            *a, **k)

        self.on_hit   += self.on_pigeon_hit
        self.on_death += self.on_pigeon_death
        for boy in boys:
            boy.on_boy_noise += self.on_boy_noise
        
        self.physical_hpr = Vec3 (90, 0, 0)
        self.params = BoidParams ()
        
        self.model_position = Vec3 (0, 0, -2)
        self.model_scale    = Vec3 (0.08, 0.08, 0.08)
        self.model_hpr      = Vec3 (180, 0, 0)
        
        self.death_sounds = map (self.load_sound, self.pigeon_death_sounds)

        self.add_state ('patrol', PatrolState)
        self.add_state ('walk',   WalkState)
        self.add_state ('follow', FollowState)
        self.add_state ('fear',   FearState)
        self.add_state ('eat',    EatState)
        self.add_state ('hit',    HitState)
        
        self.start ('walk')

    def do_update (self, timer):
        """
        Hack to avoid the tunneling effect. We manually sweep the
        collision sphere using a cylinder.
        """
        super (Pigeon, self).do_update (timer)
        vlen = self.linear_velocity.length ()
        self.geom.setParams (2., vlen * timer.delta)

    @weak_slot
    def on_pigeon_hit (self, x):
        self.enter_state ('hit')
        
    @weak_slot
    def on_boy_noise (self, boy, rad):
        if (boy.position - self.position).lengthSquared () < rad ** 2:
            if self.current.state_name != 'fear':
                self.enter_state ('fear', boy)
            else:
                self.current.restart_wait ()

    @weak_slot
    def on_pigeon_death (self):
        self.force_finish ()
        self.disable_physics ()
        random.choice (self.death_sounds).play ()


class PigeonState (State):
    
    params = BoidParams
    
    def do_setup (self, *a, **k):
        self.manager.change_params (self.params)
        self.do_pigeon_setup (*a, **k)

    def do_unsink (self, *a, **k):
        self.manager.change_params (self.params)

    do_pigeon_setup = nop
    do_pigeon_unsink = nop


class FollowState (PigeonState):    
    @weak_slot
    def on_boy_set_position (self, boy, pos):
        self.params.boid_target = pos
    def do_pigeon_setup (self, boy):
        boy.on_entity_set_position += self.on_boy_set_position

class FearState (FollowState, task.WaitTask):
    class params (BoidParams):
        boid_f_target = - 0.002
    duration = 10.

class EatState (State):
    pass

class WalkState (PigeonState):
    class params (BoidParams):
        boid_flying   = False
        boid_speed    = 10
        boid_max_far  = 300
        boid_f_bounds = 0.1

class PatrolState (PigeonState):
    class params (BoidParams):
        boid_speed  = 100.

class HitState (PigeonState, task.WaitTask):
    class params (BoidParams):
        boid_flocking = False
        boid_speed    = 1000
    duration = 5.



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
