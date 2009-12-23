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
from core.task import Task
from base.observer import make_observer

DEFAULT_KEYMAP = { 'on_move_forward'  : 'panda-w',
                   'on_move_backward' : 'panda-s',
                   'on_strafe_left'   : 'panda-q',
                   'on_strafe_right'  : 'panda-e',
                   'on_steer_left'    : 'panda-a',
                   'on_steer_right'   : 'panda-d' }

PlayerSubject, PlayerListener = make_observer (
    [ 'on_steer_left',
      'on_steer_right',
      'on_strafe_left',
      'on_strafe_right',
      'on_move_forward',
      'on_move_backward' ],
    'Player', __name__)

def times (vec, scalar):
    return map (lambda x: x * scalar, vec)

class PlayerController (PlayerListener):

    FORCE        = 1000.0
    BW_FORCE     = -1.0
    ANGLE_SPEED  = 1000.0
    STRAFE_FORCE = 1000.0
    
    def __init__ (self, entity = None, *a, **k):
        super (PlayerController, self).__init__ (*a, **k)
        self.entity = entity
        self.angle  = 0
        
    def on_steer_left (self, timer):
        self.angle += timer.delta * self.ANGLE_SPEED
        self._update_angle ()
        
    def on_steer_right (self, timer):
        self.angle -= timer.delta * self.ANGLE_SPEED
        self._update_angle ()

    def _update_angle (self):
        self.entity.set_hpr ((math.cos (self.angle), 0,
                              math.sin (self.angle)))
        
    def on_move_forward (self, timer):
        self.entity.apply_force (times (self.entity.get_hpr (), self.FORCE))
        
    def on_move_backward (self, timer):
        self.entity.apply_force (times (self.entity.get_hpr (), self.BW_FORCE))

    def on_strafe_left (self, timer):
        pass
        
    def on_strafe_right (self, timer):
        pass
    
