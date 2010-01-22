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

from base.conf import GlobalConf
from base.meta import mixin
from base.sender import AutoSender, AutoReceiver
from base.util import delayed

from core.input import InputTask
from ent.game import GameState

from camera import FastEntityFollower, SlowEntityFollower
from boy import Boy
from level import Level
from player import PlayerEntityDecorator
from pigeon import Pigeon
from flock import Flock, make_random_flock

DEBUG_INSTANCE = None

PLAYER_INPUT_MAP = {
    'on_move_forward'  : 'panda-w',
    'on_move_backward' : 'panda-s',
    'on_strafe_left'   : 'panda-a',
    'on_strafe_right'  : 'panda-d',
    'on_steer_left'    : 'panda-k',
    'on_steer_right'   : 'panda-l',
    'on_jump'          : 'panda-space',
    'on_walk'          : 'panda-c',
    'on_place_stick'   : 'panda-q',
    'on_steer'         : 'panda-mouse-move',
}

CAMERA_INPUT_MAP = {
    'on_zoom_in'       : 'panda-wheel_up',
    'on_zoom_out'      : 'panda-wheel_down',
    'on_angle_change'  : 'panda-mouse-move'
}

GameInput        = mixin (InputTask, AutoSender)
PlayerController = mixin (PlayerEntityDecorator, AutoReceiver)
CameraController = mixin (FastEntityFollower, AutoReceiver)

class Game (GameState):

    def do_setup (self):
        global DEBUG_INSTANCE
        DEBUG_INSTANCE = self
        
        cfg = GlobalConf ().child ('game')
        cfg.child ('music-volume').set_value (0.01)
        
        # Input helper
        player_input = GameInput (PLAYER_INPUT_MAP)
        camera_input = GameInput (CAMERA_INPUT_MAP)

        # TODO: Event entity to make this automatically ;)
        self.events.connect (player_input)
        self.events.connect (camera_input)
        self.tasks.add (player_input)
        self.tasks.add (camera_input)

        # Music
        music = loader.loadSfx ('snd/houmdrak.mp3')
        music.setLoop (True)
        music.play ()
        music.setVolume (cfg.child ('music-volume').value)
        print "volume: ", cfg.child ('music-volume').value
        
        # Game entities
        boy = Boy (entities = self.entities)
        flock1 = make_random_flock (self.entities, 20,
                                    boid_cls = delayed (Pigeon) (the_boy = boy))
        # flock2 = make_random_flock (self.entities, 10,
        #                             boid_cls  = delayed (Pigeon) (the_boy = boy))

        level = Level (entities = self.entities)
        boy.set_position (Vec3 (0, 70, 20))
        level.set_position (Vec3 (0, 0, 0))
        
        # Camera and player controller
        camera_ctl = CameraController (entities = self.entities,
                                       camera = base.camera)
        player_ctl = PlayerController (entities = self.entities,
                                       delegate = boy)
        boy.connect (camera_ctl)
        #flock.leader.connect (cameractl)
        camera_input.connect (camera_ctl)
        player_input.connect (player_ctl)
        
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
        self.events.event ('panda-p').connect (self.toggle_pause)
        # Preload all the shit
        map (loader.loadModel, [
            '../data/mesh/stick_arch_sub.x'
            ])
     
