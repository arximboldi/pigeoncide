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

from direct.interval.IntervalGlobal import *

from base.signal import signal
from base.sender import AutoReceiver
from base.util import printfn
from core.util import *
from core import task

from ent.entity import Entity
from ent.task import TaskEntity
from pandac.PandaModules import Vec3

from boy import Boy, DelegateBoy
from pigeon import PigeonFood

from functools import partial
from operator import add

import laser
import math
import random

action_running        = 1
action_forward        = 1 << 2
action_feeding        = 1 << 3
action_backward       = 1 << 5
action_strafe_l       = 1 << 6
action_strafe_r       = 1 << 7
action_jump           = 1 << 8
action_hit            = 1 << 9
action_feed           = 1 << 10

noise_hit   = 10.
noise_jump  = 200.
noise_run   = 50.
noise_stick = 30.
noise_throw = 10.
noise_walk  = 0.
noise_feed  = 0.

class PlayerEntityBase (TaskEntity):
    """
    Incomplete mixing requiring:
    - StandingPhisicalEntity
    - ModelPhysicalEntity
    """

    animations = [ (action_hit,      'hit'),
                   (action_feed,     'feed'),
                   (action_running,  'run'),
                   (action_forward,  'walk'),
                   (action_backward, 'walk'),
                   (0,               'idle') ]

    force              = 10000.0
    bw_force           = 10000.0
    strafe_force       = 10000.0
    jump_force         = 3000.0
    
    max_rotate_speed   = 2.0
    max_run_speed      = 60
    max_walk_speed     = 30
    steer_speed        = 0.01

    can_place_stick    = True
    
    def __init__ (self, *a, **k):
        super (PlayerEntityBase, self).__init__ (*a, **k)

        self.angle    = 0
        self.actions  = 0x0
        self.laser    = laser.Group (self.entities)
        
        self._anim_interval = None
        self._curr_anim     = 'idle'
        self._move_sounds   = map (self.load_sound,
                                   map (lambda x: "snd/movement-%i.wav" % x,
                                        range (1, 6)))
        self._run_snd_task  = self.entities.tasks.add (task.loop (
            task.run (lambda: random.choice (self._move_sounds).play ()),
            task.wait (.5)))
        self._walk_snd_task  = self.entities.tasks.add (task.loop (
            task.run (lambda: random.choice (self._move_sounds).play ()),
            task.wait (1.)))
        
        self._run_snd_task.pause ()
        self._walk_snd_task.pause ()
        
        self.update_animation ()
        
    def update_animation (self, loop = True):
        for state, anim in self.animations:
            if self.actions & state == state:
                self.change_animation (anim, loop)
                break
    
    def change_animation (self, anim, loop = True):
        if anim != self._curr_anim:
            if self._anim_interval:
                self._anim_interval.finish ()
            interv = self.model.actorInterval (anim)
            if loop:
                interv.loop ()
            else:
                interv = Sequence (interv, Func (self.update_animation))
                interv.start ()
            self._anim_interval = interv
            self._curr_anim = anim

            # hack
            if self._curr_anim == 'walk':
                self._walk_snd_task.resume ()
                self._run_snd_task.pause ()
            elif self._curr_anim == 'run':
                self._walk_snd_task.pause ()
                self._run_snd_task.resume ()
            else:
                self._walk_snd_task.pause ()
                self._run_snd_task.pause ()
    
    def start_action (self, action, loop = True):
        self.actions |= action
        self.update_animation (loop)

    def stop_action (self, action, loop = True):
        self.actions &= ~action
        self.update_animation (loop)

    def test_action (self, action):
        return self.actions & action == action
    
    def do_update (self, timer):
        super (PlayerEntityBase, self).do_update (timer)
        if self.actions & action_jump:
            self.add_force (Vec3 (0, 0, 1) * self.jump_force / timer.delta)
            self.is_on_floor_timer = 0.
            self.actions &= ~ action_jump

    def get_place_position (self, dist):
        direction = Vec3 (math.sin (self.angle), math.cos (self.angle), 0)
        return self.position + direction * dist

    @signal
    def on_place_stick_down (self):
        if self.can_place_stick:
            stick = laser.Stick (entities = self.entities)
            stick.position = self.get_place_position (5.)
            stick.hpr = self.hpr
            self.laser.add_stick (stick)
            self.emit_noise (noise_stick)
            
    def on_throw_weapon_down (self):
        weapon = self.weapon
        if not self.test_action (action_hit) and weapon:
            weapon.set_owner (None)
            self.start_action (action_hit, False)
            self.emit_noise (noise_throw)
            self.entities.tasks.add (task.sequence (
                task.wait (1.),
                task.run (lambda: self.stop_action (action_hit))))

    def on_hit_down (self):
        weapon = self.weapon

        if not self.test_action (action_hit) and weapon:
            weapon.start_hitting ()
            self.start_action (action_hit, False)
            self.emit_noise (noise_hit)
            self.entities.tasks.add (task.sequence (
                task.wait (1.),
                task.run (weapon.finish_hitting),
                task.run (lambda: self.stop_action (action_hit))))    

    def on_feed_down (self):
        if not self.test_action (action_feed):
            pos = self.get_place_position (5)
            food = PigeonFood (entities = self.entities)
            food.position = pos
            self.start_action (action_feed, False)
            self.emit_noise (noise_feed)
            self.entities.tasks.add (task.sequence (
                task.wait (1.),
                task.run (lambda: self.stop_action (action_feed))))    
    
    def on_jump_down (self):
        self.emit_noise (noise_jump)
        if self.is_on_floor:
            self.start_action (action_jump)
                
    def on_run_down (self):
        self.start_action (action_running)
        
    def on_run_up (self):
        self.stop_action (action_running)
        
    def on_move_forward_down (self):
        self.start_action (action_forward)
        
    def on_move_forward_up (self):
        self.stop_action (action_forward)
        
    def on_move_backward_down (self):
        self.start_action (action_backward)

    def on_move_backward_up (self):
        self.stop_action (action_backward)
        
    def on_steer_left (self, timer):
        self.angle -= timer.delta * self.max_rotate_speed
        
    def on_steer_right (self, timer):
        self.angle += timer.delta * self.max_rotate_speed

    def on_move_forward (self, timer):
        self.emit_move_noise ()
        self._do_force (timer, self.force, 0)

    def on_move_backward (self, timer):
        self.emit_move_noise ()
        self._do_force (timer, self.bw_force, math.pi)

    def on_strafe_right_down (self):
        self.start_action (action_strafe_r)

    def on_strafe_right_up (self):
        self.stop_action (action_strafe_r)

    def on_strafe_left_down (self):
        self.start_action (action_strafe_l)

    def on_strafe_left_up (self):
        self.stop_action (action_strafe_l)
        
    def on_strafe_left (self, timer):
        self.emit_move_noise ()
        self._do_force (timer, self.strafe_force, -math.pi/2)
        
    def on_strafe_right (self, timer):
        self.emit_move_noise ()
        self._do_force (timer, self.strafe_force, math.pi/2)

    def on_steer (self, (px, py)):
        self.angle  += px * self.steer_speed

    def emit_move_noise (self):
        self.emit_noise (noise_run if self.test_action (action_running)
                         else noise_walk)
    
    def _do_force (self, timer, force, angle):
        direction    = Vec3 (math.sin (self.angle + angle),
                             math.cos (self.angle + angle), 0)
        velocity     = self.linear_velocity
        vel_on_dir   = direction * velocity.dot (direction)

        speed_limit  = self.max_run_speed \
                       if self.actions & action_running \
                       else self.max_walk_speed 

        if vel_on_dir.lengthSquared () < speed_limit ** 2:
            self.add_force (direction * force)


class PlayerEntity (PlayerEntityBase, Boy):
    pass


class PlayerEntityDecorator (PlayerEntityBase, DelegateBoy):
    pass
