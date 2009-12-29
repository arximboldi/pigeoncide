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

from pandac.PandaModules import Vec4, Vec3, AmbientLight, PointLight

from base.meta import mixin
from base.sender import AutoSender, AutoReceiver
from core.keyboard import KeyboardTask
from ent.game import GameState
from ent.camera import SlowEntityFollower
from boy import Boy
from level import Level
from player import DelegatePlayerEntity


DEFAULT_KEYMAP = { 'on_move_forward'  : 'panda-w',
                   'on_move_backward' : 'panda-s',
                   'on_strafe_left'   : 'panda-q',
                   'on_strafe_right'  : 'panda-e',
                   'on_steer_left'    : 'panda-a',
                   'on_steer_right'   : 'panda-d',
                   'on_jump'          : 'panda-space',
                   'on_walk'          : 'panda-c' }

PlayerKeyboard = mixin (KeyboardTask, AutoSender)
PlayerController = mixin (DelegatePlayerEntity, AutoReceiver)

class Game (GameState):

    def setup (self):
        keyboard = PlayerKeyboard (DEFAULT_KEYMAP)

        base.setBackgroundColor (Vec4 (.4, .6, .9, 1))
        
        self.events.connect (keyboard)
        self.tasks.add (keyboard)

        boy = Boy (entities = self.entities)
        level = Level (entities = self.entities)
        
        boy.set_position ((0, 70, 20))
        level.set_position ((0, 0, -100))
        
        boy.connect (SlowEntityFollower (camera = base.camera))
        keyboard.connect (PlayerController (entities = self.entities,
                                            delegate = boy))
        
        plightnode = PointLight ("point light")
        plightnode.setAttenuation (Vec3 (1, 0.0000005, 0.0000001))
        plight = render.attachNewNode (plightnode)
        plight.setPos (100, -100, 1000)

        alightnode = AmbientLight ("ambient light")
        alightnode.setColor (Vec4 (0.1, 0.1, 0.1, 1))
        alight = render.attachNewNode (alightnode)

        render.setLight (alight)
        render.setLight (plight)

        self.events.event ('panda-escape').connect (self.kill)
    
