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
from base.meta import mixin, Mockup
from base.sender import AutoSender, AutoReceiver
from base.util import delayed
from base.signal import weak_slot

from core import task
from core import shader
from core.input import KeyboardTask
from ent.game import GameState, LightGameState

from loader import LoaderInterState
from camera import FastEntityFollower, SlowEntityFollower
from boy import Boy
from level import Level
from player import PlayerEntityDecorator
from pigeon import Pigeon
from flock import FlockEntity, make_random_flock
from hud import Hud
import ui

PLAYER_INPUT_MAP = {
    'on_move_forward'  : 'panda-w',
    'on_move_backward' : 'panda-s',
    'on_strafe_left'   : 'panda-a',
    'on_strafe_right'  : 'panda-d',
    'on_steer_left'    : 'panda-k',
    'on_steer_right'   : 'panda-l',
    'on_jump'          : 'panda-space',
    'on_run'           : 'panda-c',
    'on_hit'           : 'panda-e',
    'on_place_stick'   : 'panda-q',
    'on_steer'         : 'panda-mouse-move',
}

CAMERA_INPUT_MAP = {
    'on_zoom_in'       : 'panda-wheel_up',
    'on_zoom_out'      : 'panda-wheel_down',
    'on_angle_change'  : 'panda-mouse-move'
}

GameInput        = mixin (KeyboardTask, AutoSender)
PlayerController = mixin (PlayerEntityDecorator, AutoReceiver)
CameraController = mixin (FastEntityFollower, AutoReceiver)


class GameIntro (LightGameState):

    def do_setup (self):
        self.black = ui.ImageEntity (entities = self.entities,
                                     image    = 'obj/black.png')
        self.black.alpha = 1.0
        self.black.fade_out ()
        
        self.text = ui.TextEntity (
            entities     = self.entities,
            font         = 'font/gilles.ttf',
            fg           = (1, 1, 1, 1),
            shadow       = (.5, 0, 0, 1),
            shadowOffset = (.08, .08),
            wordwrap     = 30,
            scale        = 0.1,
            text         =
            (('You have to kill %i pigeons in this level...\n' +
             'Can you make it?')
             % self.parent_state.total_pigeons))

        self.help_text = ui.TextEntity (
            entities = self.entities,
            font     = 'font/alte-regular.ttf',
            fg       = (1, 1, 0, .9),
            pos      = (0, -.9),
            scale    = 0.05,
            text     = 'Press enter to continue...')
        
        self.help_text.fade_in (duration = 1)
        self.text.fade_in (duration = 1)

        self.events.event ('panda-enter').connect (self.finish_intro)
        self.events.event ('panda-escape').connect (self.kill)
        self.events.event ('panda-escape').connect (self.parent_state.kill)

        self.parent_state.camera_ctl.loop_angle (duration = 4.)
        
    def finish_intro (self):
        self.help_text.fade_out ()
        self.text.fade_out ().add_next (task.run (self.kill))
        self.parent_state.camera_ctl.restore_angle ()


class GameFail (LightGameState):
    pass


class GameWin (LightGameState):
    pass


class GameQuit (LightGameState):
    pass


class Game (GameState):

    def do_setup (self, level):
        super (Game, self).do_setup ()
        
        self.level = level
        
        self.setup_panda ()
        self.level.setup_entities (self.entities)
        self.setup_input ()
        self.setup_controllers ()
        self.setup_hud ()
        self.setup_logic ()

        self.events.event ('panda-escape').connect (self.kill)
        self.events.event ('panda-p').connect (self.toggle_pause)
        
        self.manager.enter_state (GameIntro)

    @weak_slot
    def on_kill_pigeon (self):
        self.hud.dec_counter ('pigeons', 1)
        self.dead_pigeons += 1
        if self.dead_pigeons >= self.total_pigeons:
            self.win_game ()

    @weak_slot
    def on_kill_boy (self):
        self.fail_game ("kill-boy")

    @weak_slot
    def on_finish_time (self):
        self.fail_game ("finish-time")

    @weak_slot
    def on_place_stick (self):
        if self.player_ctl.can_place_stick:
            self.num_sticks -= 1
            if self.num_sticks == 0:
                self.player_ctl.can_place_stick = False
            self.hud.set_counter ('sticks', self.num_sticks)

    def highlight_stick_task (self, timer):
        pos = self.player_ctl.get_stick_position ()
        best = self.player_ctl.laser.best_stick (pos)
        if best != self._curr_best_stick:
            if self._curr_best_stick:
                self._curr_best_stick.unhighlight ()
            if self.player_ctl.can_place_stick:
                self._curr_best_stick = best
                if best:
                    best.highlight ()
        return task.running
    
    def win_game (self):
        print "win-game"

    def fail_game (self, reason):
        print "fail-game: ", reason
        
    def do_update (self, timer):
        super (Game, self).do_update (timer)

    def setup_panda (self):
        panda = self.manager.panda
        shader.enable_glow (panda)        
        panda.relative_mouse ()
        panda.loop_music (self.level.music)

    def setup_input (self):
        self.player_input = GameInput (PLAYER_INPUT_MAP)
        self.camera_input = GameInput (CAMERA_INPUT_MAP)
        self.events.connect (self.player_input)
        self.events.connect (self.camera_input)
        self.tasks.add (self.player_input)
        self.tasks.add (self.camera_input)        

    def setup_controllers (self):
        self.camera_ctl = CameraController (
            entities = self.entities,
            camera = base.camera)
        self.player_ctl = PlayerController (
            entities = self.entities,
            delegate = self.level.boy)
        self.level.boy.connect (self.camera_ctl)
        self.camera_input.connect (self.camera_ctl)
        self.player_input.connect (self.player_ctl)

    def setup_hud (self):
        self.hud = Hud (entities = self.entities)
        self.hud.add_counter ('clock',   'hud/clock.png')
        self.hud.add_counter ('pigeons', 'hud/pigeon.png')
        self.hud.add_counter ('sticks',  'hud/stick.png')
        self.hud.hide ()
    
    def setup_logic (self):
        total_pigeons = 0
        for f in self.level.flocks:
            total_pigeons += len (f.boids)
            for b in f.boids:
                b.on_death += self.on_kill_pigeon
        
        self.total_pigeons = total_pigeons
        self.dead_pigeons = 0
        self.level.boy.on_death += self.on_kill_boy

        self.num_sticks = self.level.max_sticks
        self.player_ctl.on_place_stick_down += self.on_place_stick
        self.hud.set_counter ('sticks', self.num_sticks)
        
        self.timer = self.tasks.add (
            task.TimerTask (time = self.level.max_time))
        self.timer.on_tick = lambda: self.hud.set_counter (
            'clock', int (self.timer.remaining))
        self.timer.on_finish = self.on_finish_time

        self.tasks.add (self.highlight_stick_task)
        self._curr_best_stick = None
        
    def do_sink (self):
        super (Game, self).do_sink ()
        self.events.quiet = True
        self.hud.soft_hide ()
        self.timer.pause ()
        
    def do_unsink (self):
        super (Game, self).do_unsink ()
        self.events.quiet = False
        self.hud.soft_show ()
        self.timer.resume ()
        
    def do_release (self):
        self.level.dispose () # TODO: To entity!
        shader.disable_glow (self.manager.panda)
        super (Game, self).do_release ()


class LoadGame (LoaderInterState):
    load_data    = Level
    next_state   = Game
