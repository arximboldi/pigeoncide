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

import math

from base.sender import AutoReceiver
from core.util import *
from ent.entity import *
from ent.physical import (StandingPhysicalEntity,
                          DelegateStandingPhysicalEntity)
from ent.panda import ActorEntity, DelegateActorEntity
from pandac.PandaModules import Vec3

import laser
import math

is_walking        = 0x0001
is_forward        = 0x0002
is_feeding        = 0x0004
is_idle           = 0x0008
is_backward       = 0x0020
is_strafe_l       = 0x0040
is_strafe_r       = 0x0080


class PlayerEntityBase (Entity):
    """
    Incomplete mixing requiring:
    - StandingPhisicalEntity
    - ModelPhysicalEntity
    """

    anim_run   = 'run'
    anim_walk  = 'walk'
    anim_stand = 'idle'

    force              = 10000.0
    bw_force           = 10000.0
    strafe_force       = 10000.0
    jump_force         = 10000.0
    
    max_rotate_speed   = 2.0
    max_run_speed      = 60
    max_walk_speed     = 30
    steer_speed        = 0.01
    
    def __init__ (self, *a, **k):
        super (PlayerEntityBase, self).__init__ (*a, **k)
        self.angle    = 0
        self.actions  = 0x0
        self.laser    = laser.Group (self.entities)
        self.model.loop (self.anim_stand)
                
    def on_place_stick_down (self):
        stick = laser.Stick (entities = self.entities)
        direction = Vec3 (math.sin (self.angle), math.cos (self.angle), 0)

        stick.position = self.position + direction * 5
        stick.hpr = self.hpr

        self.laser.add_stick (stick)
        
    @property
    def is_moving (self):
        return (self.actions & is_forward)  or \
               (self.actions & is_backward) or \
               (self.actions & is_strafe_r) or \
               (self.actions & is_strafe_l)

    def animate_movement (self):
        self.model.loop (self.anim_walk
                         if self.actions & is_walking
                         else self.anim_run)

    def on_walk_down (self):
        self.actions |= is_walking
        if self.is_moving:
            self.model.loop (self.anim_walk)
        
    def on_walk_up (self):
        self.actions &= ~ is_walking
        if self.is_moving:
            self.model.loop (self.anim_run)
            
    def on_move_forward_down (self):
        self.actions |= is_forward
        self.animate_movement ()
        
    def on_move_forward_up (self):
        self.actions &= ~ is_forward
        if not self.is_moving:
            self.model.loop (self.anim_stand)
        
    def on_move_backward_down (self):
        self.actions |= is_backward
        self.animate_movement ()

    def on_move_backward_up (self):
        self.actions &= ~ is_backward
        if not self.is_moving:
            self.model.loop (self.anim_stand)
    
    def on_steer_left (self, timer):
        self.angle -= timer.delta * self.max_rotate_speed
        
    def on_steer_right (self, timer):
        self.angle += timer.delta * self.max_rotate_speed

    def on_move_forward (self, timer): 
        self._do_force (timer, self.force, 0)

    def on_move_backward (self, timer):
        self._do_force (timer, self.bw_force, math.pi)

    def on_strafe_right_down (self):
        self.actions |= is_strafe_r
        self.animate_movement ()

    def on_strafe_right_up (self):
        self.actions &= ~ is_strafe_r
        if not self.is_moving:
            self.model.loop (self.anim_stand)

    def on_strafe_left_down (self):
        self.actions |= is_strafe_l
        self.animate_movement ()

    def on_strafe_left_up (self):
        self.actions &= ~ is_strafe_l
        if not self.is_moving:
            self.model.loop (self.anim_stand)
        
    def on_strafe_left (self, timer):
        self._do_force (timer, self.strafe_force, -math.pi/2)
        
    def on_strafe_right (self, timer):
        self._do_force (timer, self.strafe_force, math.pi/2)

    def on_steer (self, (px, py)):
        self.angle  += px * self.steer_speed
    
    def _do_force (self, timer, force, angle):
        direction    = Vec3 (math.sin (self.angle + angle),
                             math.cos (self.angle + angle), 0)
        velocity     = self.linear_velocity
        vel_on_dir   = direction * velocity.dot (direction)

        speed_limit  = self.max_walk_speed \
                       if self.actions & is_walking \
                       else self.max_run_speed 

        if vel_on_dir.lengthSquared () < speed_limit ** 2:
            self.add_force (direction * force)


class PlayerEntity (
    PlayerEntityBase,
    StandingPhysicalEntity,
    ActorEntity):
    pass


class PlayerEntityDecorator (
    PlayerEntityBase,
    DelegateStandingPhysicalEntity,
    DelegateActorEntity):
    pass
