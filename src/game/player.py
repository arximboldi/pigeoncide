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
from core.task import Task

from ent.entity import *
from ent.physical import (StandingPhysicalEntity,
                          DelegateStandingPhysicalEntity)
from ent.panda import ModelEntity, DelegateModelEntity
from pandac.PandaModules import Vec3


_IS_WALKING        = 0x0001
_IS_FORWARD        = 0x0002
_IS_FEEDING        = 0x0004
_IS_IDLE           = 0x0008
_IS_BACKWARD       = 0x0020


class PlayerEntityBase (Entity):
    """
    Incomplete mixing requiring:
    - StandingPhisicalEntity
    - ModelPhysicalEntity
    """
    
    force              = 1000000.0
    bw_force           = 1000000.0
    strafe_force       = 1000000.0
    jump_force         = 1000000.0
    
    max_rotate_speed   = 2.0
    max_run_speed_sq   = 500000
    max_walk_speed_sq  = 100000

    @property
    def is_moving (self):
        return (self.actions & _IS_FORWARD) or \
               (self.actions & _IS_BACKWARD)

    def __init__ (self, *a, **k):
        super (PlayerEntityBase, self).__init__ (*a, **k)
        self.angle    = 0
        self.actions  = 0x0

    def on_walk_down (self):
        self.actions |= _IS_WALKING
        if self.is_moving:
            self.model.loop ('walk')
        
    def on_walk_up (self):
        self.actions &= ~_IS_WALKING
        if self.is_moving:
            self.model.loop ('run')
            
    def on_move_forward_down (self):
        self.actions |= _IS_FORWARD
        self.model.loop (
            'walk' if self.actions & _IS_WALKING else 'run')
        
    def on_move_forward_up (self):
        self.actions &= ~_IS_FORWARD
        if not self.is_moving:
            self.model.stop ()
        
    def on_move_backward_down (self):
        self.actions |= _IS_BACKWARD
        self.model.loop (
            'walk' if self.actions & _IS_WALKING else 'run')

    def on_move_backward_up (self):
        self.actions &= ~_IS_BACKWARD
        if not self.is_moving:
            self.model.stop ()
        
    def on_steer_left (self, timer):
        self.angle -= timer.delta * self.max_rotate_speed
        
    def on_steer_right (self, timer):
        self.angle += timer.delta * self.max_rotate_speed

    def on_move_forward (self, timer): 
        self._do_force (timer, self.force, 1.0)

    def on_move_backward (self, timer):
        self._do_force (timer, self.bw_force, -1.0)
        
    def on_strafe_left (self, timer):
        pass
        
    def on_strafe_right (self, timer):
        pass

    def _do_force (self, timer, force, fact):
        direction = Vec3 (fact * math.sin (self.angle),
                          fact * math.cos (self.angle), 0)
        speed     = self.linear_velocity
        speeddir  = speed * speed.dot (direction)
        sqlen     = speeddir.lengthSquared ()
        
        if (self.actions & _IS_WALKING and
            sqlen < self.max_walk_speed_sq) or \
           (~ self.actions & _IS_WALKING and
            sqlen < self.max_run_speed_sq):
            self.add_force (direction * force * timer.delta)


class PlayerEntity (
    PlayerEntityBase,
    StandingPhysicalEntity,
    ModelEntity):
    pass


class DelegatePlayerEntity (
    PlayerEntityBase,
    DelegateStandingPhysicalEntity,
    DelegateModelEntity):
    pass
