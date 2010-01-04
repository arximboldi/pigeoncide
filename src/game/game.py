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
from core.input import InputTask
from ent.game import GameState

from camera import FastEntityFollower, SlowEntityFollower
from boy import Boy
from level import Level
from player import DelegatePlayerEntity
from pigeon import Pigeon
from flock import make_random_flock

DEFAULT_INPUT_MAP = {

    # player control
    'on_move_forward'  : 'panda-w',
    'on_move_backward' : 'panda-s',
    'on_strafe_left'   : 'panda-o',
    'on_strafe_right'  : 'panda-p',
    'on_steer_left'    : 'panda-a',
    'on_steer_right'   : 'panda-d',
    'on_jump'          : 'panda-space',
    'on_walk'          : 'panda-c',
    'on_place_stick'   : 'panda-q',
    
    # camera control
    'on_zoom_in'       : 'panda-wheel_up',
    'on_zoom_out'      : 'panda-wheel_down',
    'on_angle_change'  : 'panda-mouse-move'

    }

GameInput        = mixin (InputTask, AutoSender)
PlayerController = mixin (DelegatePlayerEntity, AutoReceiver)
CameraController = mixin (FastEntityFollower, AutoReceiver)

class Game (GameState):

    def setup (self):
        # Input helper
        ginput = GameInput (DEFAULT_INPUT_MAP)        
        self.events.connect (ginput)
        self.tasks.add (ginput)

        # Preload all the shit
        map (loader.loadModel, [
            '../data/mesh/stick_arch_sub.x'
            ])
        
        # Game entities
        flock = make_random_flock (self.entities, 20,
                                   Vec3 (0, 0, 300), 100, Pigeon)
        boy = Boy (entities = self.entities)
        level = Level (entities = self.entities)
        boy.set_position ((0, 70, 20))
        level.set_position ((0, 0, 0))
        flock.target = boy
        
        # Camera and player controller
        cameractl = CameraController (camera = base.camera)
        playerctl = PlayerController (entities = self.entities,
                                      delegate = boy)
        boy.connect (cameractl)
        #flock.leader.connect (cameractl)
        ginput.connect (cameractl)
        ginput.connect (playerctl)
        
        # Aesthetics
        plightnode = PointLight ("point light")
        plightnode.setAttenuation (Vec3 (1, 0.0000005, 0.0000001))
        plight = render.attachNewNode (plightnode)
        plight.setPos (100, -100, 1000)
        alightnode = AmbientLight ("ambient light")
        alightnode.setColor (Vec4 (0.1, 0.1, 0.1, 1))
        alight = render.attachNewNode (alightnode)
        render.setLight (alight)
        render.setLight (plight)
        base.setBackgroundColor (Vec4 (.4, .6, .9, 1))

        # Helper
        self.events.event ('panda-escape').connect (self.kill)
    
