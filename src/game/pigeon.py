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

from base.util import *

from ent.observer import ObservableSpatialEntity
from ent.panda import ActorEntity, ModelEntity
from ent.physical import (DynamicPhysicalEntity, StandingPhysicalEntity,
                          OnFloorEntity)

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

class PigeonFood (ModelEntity,
                  DynamicPhysicalEntity,
                  ObservableSpatialEntity):

    food_model = 'obj/food.egg'
    amount     = 1.0
    food_scale = 0.5
    
    def __init__ (self, *a, **k):
        super (PigeonFood, self).__init__ (
            model = self.food_model,
            geometry = geom.box (2, 2, 0.5),
            *a, **k)
        self.model.setTexture (loader.loadTexture ('obj/food.png'))
        self.model_scale = self.food_scale
        # A bit hackish, I guess
        self.entities.game.pigeon_food.append (self)
        
    def eat (self, cnt):
        self.amount -= cnt
        if self.amount <= 0.0:
            self.dispose ()
        else:
            s = self.amount * self.food_scale
            self.model_scale = Vec3 (s, s, s)

    def dispose (self):
        self.entities.game.pigeon_food.remove (self)
        super (PigeonFood, self).dispose ()


class Pigeon (BoidEntity,
              ActorEntity,
              KillableEntity,
              StateManager,
              OnFloorEntity,
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

    pigeon_sweeping = True
    pigeon_min_eat_distance = 300.
    pigeon_z_limit = -50.
    
    def __init__ (self,
                  model = pigeon_model,
                  anims = pigeon_anims,
                  boys  = [],
                  *a, **k):
        super (Pigeon, self).__init__ (
            geometry = geom.capsule (2, 1),
            #mass     = mass.sphere (1, 2),
            model    = model,
            anims    = anims,
            category = pigeon_category,
            *a, **k)

        self.on_is_on_floor_change += self.on_pigeon_is_on_floor
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

        self.add_state ('fly',    FlyState)
        self.add_state ('walk',   WalkState)
        self.add_state ('follow', FollowState)
        self.add_state ('fear',   FearState)
        self.add_state ('eat',    EatState)
        self.add_state ('hit',    HitState)
        self.add_state ('land',   LandState)
        self.add_state ('return', ReturnState)
        
        self.model.loop ('fly')
        self.curr_animation = 'fly'
        self.anim_speed = 50
        
        self.start ('land')
                
    def do_update (self, timer):
        """
        Hack to avoid the tunneling effect. We manually sweep the
        collision sphere using a cylinder.
        """
        super (Pigeon, self).do_update (timer)
        vlen = self.linear_velocity.length ()
        if self.pigeon_sweeping:
            self.geom.setParams (2., vlen * timer.delta)
        self.model.setPlayRate (vlen / self.anim_speed, self.curr_animation)
        self.check_limits ()

    @weak_slot
    def on_pigeon_is_on_floor (self, who, val):
        if val and self.current and self.current.state_name == 'land':
            self.change_state ('walk')
            
        if val and self.curr_animation != 'walk':
            self.model.loop ('walk')
            self.curr_animation = 'walk'
        elif not val and self.curr_animation != 'fly':
            self.model.loop ('fly')
            self.curr_animation = 'fly'
    
    @weak_slot
    def on_pigeon_hit (self, x):
        self.enter_state ('hit')
        
    @weak_slot
    def on_boy_noise (self, boy, rad):
        if distance_sq (boy.position, self.position) < rad ** 2:
            if self.current.state_name != 'fear':
                self.enter_state ('fear', boy)
            else:
                self.current.restart_wait ()
    
    @weak_slot
    def on_pigeon_death (self):
        self.force_finish ()
        self.disable_physics ()
        random.choice (self.death_sounds).play ()

    def find_food (self):
        food = self.entities.game.pigeon_food
        best = None
        bestdist = 1000000.
        pos = self.position
        for f in food:
            dist = distance_sq (f.position, pos)
            if dist < self.pigeon_min_eat_distance ** 2 and dist < bestdist:
                bestdist = dist
                best = f
        return best

    def check_food (self, change = False):
        best = self.find_food ()
        if best:
            self.enter_state ('eat', best)
    
    def check_limits (self):
        pos = self.position
        if pos.getZ () < self.pigeon_z_limit:
            print "WARNING! WARNING!", self, pos
            if self.current.state_name != 'return':
                self.enter_state ('return')

class PigeonState (State, BoidParams):

    anim_speed = 50.

    def do_setup (self, *a, **k):
        self.manager.change_params (self)
        self.manager.anim_speed = self.anim_speed
        self.do_pigeon_setup (*a, **k)
        
    def do_sink (self):
        self.pause ()

    def do_unsink (self, *a, **k):
        self.manager.change_params (self)
        self.manager.anim_speed = self.anim_speed
        self.resume ()
        self.do_pigeon_unsink (self)
        
    def do_update (self, timer):
        super (PigeonState, self).do_update (timer)

    def do_release (self):
        self.do_pigeon_release ()
        
    do_pigeon_release = nop
    do_pigeon_setup   = nop
    do_pigeon_unsink  = nop


class FollowState (PigeonState):    

    @weak_slot
    def on_target_set_position (self, target, pos):
        self.boid_target = pos

    def do_pigeon_setup (self, target):
        target.on_entity_set_position += self.on_target_set_position
        self.boid_target = target.position


class FearState (FollowState, task.WaitTask):

    anim_speed = 50.
    duration = 2.
    boid_f_target = - 0.002
    boid_speed = 200


class EatState (FollowState):

    boid_flying   = False
    boid_speed    = 20
    boid_f_target   = 0.1
    boid_f_randomness = 0.
    boid_power = 100.
        
    glutony      = 0.3
    eat_distance = 5
    anim_speed   = 10.

    def do_pigeon_setup (self, target):
        super (EatState, self).do_pigeon_setup (target)
        self.happy_meal = target

    def do_update (self, timer):
        super (EatState, self).do_update (self)
        best = self.manager.find_food ()
        if best != self.happy_meal and best:
            self.manager.change_state ('eat', best)
        elif self.happy_meal:
            if distance_sq (self.happy_meal.position, self.manager.position) < \
               self.eat_distance ** 2:
                self.boid_speed = 0.001
                self.boid_power = 0.001
                self.happy_meal.eat (timer.delta * self.glutony)
        else:
            self.manager.leave_state ()


class PatrolState (PigeonState):

    def do_pigeon_setup (self):
        super (PatrolState, self).do_pigeon_setup ()
        self.tasks.add (task.sequence (
            task.wait (random.uniform (5., 30)),
            task.run (self.next_state)))

    def do_update (self, timer):
        super (PatrolState, self).do_update (timer)
        self.manager.check_food ()

    def next_state (self):
        self.manager.change_state (
            'land' if self.state_name == 'fly' else 'fly')


class WalkState (PatrolState):

    anim_speed    = 7.

    boid_flying   = False
    boid_speed    = 10
    boid_max_far  = 500
    boid_f_bounds = 0.001
    boid_power    = 100.
    boid_f_randomness = 0.


class ReturnState (PigeonState):

    anim_speed    = 50
    
    boid_max_far  = 100
    boid_f_bounds = 0.1
    boid_center   = Vec3 (0, 0, 200)
    
    def do_update (self, timer):
        super (ReturnState, self).do_update (timer)
        if distance_sq (self.manager.position, self.boid_center) < \
               self.boid_max_far ** 2:
            self.manager.leave_state ()


class LandState (PigeonState):
    
    anim_speed = 50
    boid_speed = 60    
    boid_max_far  = 500
    boid_f_bounds = 0.001
    boid_flying   = False

class FlyState (PatrolState):

    anim_speed  = 50.
    boid_speed  = 80.


class HitState (PigeonState):

    boid_flocking = False
    boid_flying   = False
    boid_speed    = 1000

    def do_pigeon_setup (self):
        self.tasks.add (task.sequence (task.wait (2.), task.run (self.kill)))
        self.manager.pigeon_sweeping = False

    def do_pigeon_release (self):
        self.manager.pigeon_sweeping = True
