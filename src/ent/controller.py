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
from pandac.PandaModules import Vec3

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

def vec2tuple (vec):
    return (vec.getX (), vec.getY (), vec.getZ ())

class PlayerController (PlayerListener):

    FORCE        = 1000000.0
    BW_FORCE     = 1000000.0
    ANGLE_SPEED  = 2.0
    STRAFE_FORCE = 1000.0
    MAX_SPEED    = 100000
    
    def __init__ (self, entity = None, *a, **k):
        super (PlayerController, self).__init__ (*a, **k)
        self.entity = entity
        self.entity.angle  = 0
        
    def on_steer_left (self, timer):
        self.entity.angle -= timer.delta * self.ANGLE_SPEED
        
    def on_steer_right (self, timer):
        self.entity.angle += timer.delta * self.ANGLE_SPEED

    def on_move_forward (self, timer):
        self._do_force (timer, self.FORCE, 1.0)
        
    def on_move_backward (self, timer):
        self._do_force (timer, self.BW_FORCE, -1.0)

    def _do_force (self, timer, force, fact):
        direction = Vec3 (fact * math.sin (self.entity.angle),
                          fact * math.cos (self.entity.angle), 0)
        speed     = Vec3 (self.entity.speed)
        speeddir  = speed * speed.dot (direction)
        
        if speeddir.lengthSquared () < self.MAX_SPEED:
            self.entity.apply_force (vec2tuple (
                direction * force * timer.delta))
        
    def on_strafe_left (self, timer):
        pass
        
    def on_strafe_right (self, timer):
        pass
    
