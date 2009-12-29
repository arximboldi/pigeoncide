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
from base.observer import make_observer
from pandac.PandaModules import Vec3
from heapq import *

PlayerSubject, PlayerListener = make_observer (
    [ 'on_steer_left',
      'on_steer_right',
      'on_strafe_left',
      'on_strafe_right',
      'on_move_forward',
      'on_move_backward' ],
    'Player', __name__)

_IS_WALKING        = 0x0001
_IS_FORWARD        = 0x0002
_IS_FEEDING        = 0x0004
_IS_IDLE           = 0x0008
_IS_BACKWARD       = 0x0020

class PlayerController (AutoReceiver):

    FORCE             = 1000000.0
    BW_FORCE          = 1000000.0
    STRAFE_FORCE      = 1000000.0
    JUMP_FORCE        = 1000000.0
    
    ROTATE_SPEED      = 2.0

    MAX_SPEED_SQ      = 500000
    MAX_WALK_SPEED_SQ = 100000

    @property
    def is_moving (self):
        return (self.actions & _IS_FORWARD) or \
               (self.actions & _IS_BACKWARD)

    def __init__ (self, entity = None, *a, **k):
        super (PlayerController, self).__init__ (*a, **k)
        self.entity        = entity
        self.entity.angle  = 0
        self.actions       = 0x0

    def on_walk_down (self):
        self.actions |= _IS_WALKING
        if self.is_moving:
            self.entity.model.loop ('walk')
        
    def on_walk_up (self):
        self.actions &= ~_IS_WALKING
        if self.is_moving:
            self.entity.model.loop ('run')
            
    def on_move_forward_down (self):
        self.actions |= _IS_FORWARD
        self.entity.model.loop (
            'walk' if self.actions & _IS_WALKING else 'run')
        
    def on_move_forward_up (self):
        self.actions &= ~_IS_FORWARD
        if not self.is_moving:
            self.entity.model.stop ()
        
    def on_move_backward_down (self):
        self.actions |= _IS_BACKWARD
        self.entity.model.loop (
            'walk' if self.actions & _IS_WALKING else 'run')

    def on_move_backward_up (self):
        self.actions &= ~_IS_BACKWARD
        if not self.is_moving:
            self.entity.model.stop ()
        
    def on_steer_left (self, timer):
        self.entity.angle -= timer.delta * self.ROTATE_SPEED
        
    def on_steer_right (self, timer):
        self.entity.angle += timer.delta * self.ROTATE_SPEED

    def on_move_forward (self, timer): 
        self._do_force (timer, self.FORCE, 1.0)

    def on_move_backward (self, timer):
        self._do_force (timer, self.BW_FORCE, -1.0)
        
    def on_strafe_left (self, timer):
        pass
        
    def on_strafe_right (self, timer):
        pass

    def _do_force (self, timer, force, fact):
        direction = Vec3 (fact * math.sin (self.entity.angle),
                          fact * math.cos (self.entity.angle), 0)
        speed     = Vec3 (self.entity.speed)
        speeddir  = speed * speed.dot (direction)
        sqlen     = speeddir.lengthSquared ()
        
        if (self.actions & _IS_WALKING and
            sqlen < self.MAX_WALK_SPEED_SQ) or \
           (~ self.actions & _IS_WALKING and
            sqlen < self.MAX_SPEED_SQ):
            self.entity.apply_force (direction * force * timer.delta)

