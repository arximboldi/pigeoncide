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

"""
Import this or patch_messenger before any other module usin Panda base.
"""

import patch_messenger

from base.conf import GlobalConf
from timer import Timer
from input import MouseTask
import task

from direct.showbase.ShowBase import ShowBase
from direct.showbase.Audio3DManager import Audio3DManager
from direct.filter.CommonFilters import CommonFilters
from pandac.PandaModules import *

class PandaController (object):

    DEFAULT_FULLSCREEN = False
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600
    DEFAULT_FPS = 60
    DEFAULT_FRAME_METER = False
    DEFAULT_MUSIC_VOLUME = .3
    DEFAULT_SOUND_VOLUME = .1
    DEFAULT_MAX_DELTA = 1. / 20.
    DEFAULT_SHADERS = True
    
    def __init__ (self):
        super (PandaController, self).__init__ ()
        self._timer = Timer ()
        self._timer.max_delta = self.DEFAULT_MAX_DELTA
        self._tasks = task.TaskGroup ()
        self._tasks.add (self._panda_task)
        self._music = None
        self._mouse_task = None
        self._relative_mouse = False
        
    @property
    def timer (self):
        return self._timer

    @property
    def tasks (self):
        return self._tasks

    def start (self, title):
        cfg = GlobalConf ().child ('panda') 

        self.set_defaults (cfg)
        self.base = ShowBase ()
        self.base.disableMouse ()
        self.audio = self.base.sfxManagerList [0]
        self.audio3d = Audio3DManager (self.audio, camera)
        self.audio3d.setListenerVelocityAuto ()
        self.audio3d.setDropOffFactor (0.1) # HACK
        
        self.create_properties (title)
        self.update_properties (cfg)
        self.listen_conf (cfg)

        loadPrcFileData ("", "interpolate-frames 1")
        loadPrcFileData ("", "support-threads #f")
        path = getModelPath ()
        path.prependPath ('./data')
                
        self.base.enableParticles ()
        
    def loop (self):        
        self._timer.reset ()
        self._timer.loop (self._loop_fn)

    def _loop_fn (self, timer):
        task_count = 1               # _panda_task
        if self._relative_mouse:
            task_count += 1          # _mouse_task
        if self._tasks.count > task_count:
            return self._tasks.update (timer)
        return False
    
    def set_defaults (self, cfg):
        cfg.child ('fps').default (self.DEFAULT_FPS)
        cfg.child ('width').default (self.DEFAULT_WIDTH)
        cfg.child ('height').default (self.DEFAULT_HEIGHT)
        cfg.child ('fullscreen').default (self.DEFAULT_FULLSCREEN)
        cfg.child ('frame-meter').default (self.DEFAULT_FRAME_METER)
        cfg.child ('music-volume').default (self.DEFAULT_MUSIC_VOLUME)
        cfg.child ('sound-volume').default (self.DEFAULT_SOUND_VOLUME)
                
    def listen_conf (self, cfg):
        cfg.on_conf_nudge += self.update_properties
        
        cfg.child ('fps').on_conf_change += self.update_fps
        cfg.child ('frame-meter').on_conf_change += self.update_frame_meter
        cfg.child ('music-volume').on_conf_change += self.update_music_volume
        cfg.child ('sound-volume').on_conf_change += self.update_sound_volume

        self.audio.setVolume (cfg.child ('sound-volume').value)
    
    def create_properties (self, title):
        self._prop = WindowProperties ()
        self._prop.setTitle (title)
        
    def relative_mouse (self):
        if not self._relative_mouse:
            self._prop.setCursorHidden (True)
            self._prop.setMouseMode (WindowProperties.MRelative)
            self.base.win.requestProperties (self._prop)
            self._mouse_task = self._tasks.add (MouseTask ())
            self._mouse_task.on_mouse_move += lambda x, y: \
                messenger.send ('mouse-move', [(x, y)])
            self._relative_mouse = True
        
    def absolute_mouse (self):
        if self._relative_mouse:
            self._relative_mouse = False
            if self._mouse_task:
                self._mouse_task.kill ()
            self._prop.setCursorHidden (False)
            self._prop.setMouseMode (WindowProperties.MAbsolute)
            self.base.win.requestProperties (self._prop)
    
    def has_shaders (self):
        return self.base.win.getGsg().getSupportsBasicShaders() == 0
        
    def update_properties (self, cfg):
        self._prop.setSize (cfg.child ('width').value,
                            cfg.child ('height').value)
        self._prop.setFullscreen (cfg.child ('fullscreen').value)
        self.base.win.requestProperties (self._prop)
        
        self._timer.fps = cfg.child ('fps').value
        self.base.setFrameRateMeter (cfg.child ('frame-meter').value)

    def update_frame_meter (self, cfg):
        self.base.setFrameRateMeter (cfg.value)

    def update_fps (self, cfg):
        self._timer.fps = cfg.value

    def update_music_volume (self, cfg):
        if self._music:
            self._music.setVolume (cfg.value)

    def update_sound_volume (self, cfg):
        if self.audio:
            self.audio.setVolume (cfg.value)

    def _panda_task (self, timer):
        taskMgr.step ()
        return task.running

    def set_background_color (self, *color):
        base.setBackgroundColor (*color)
    
    def loop_music (self, file):
        if self._music:
            self._music.setLoop (False)
            self.tasks.add (task.sequence (
                task.linear (self._music.setVolume,
                             self._music.getVolume (), 0.0)))

        volume = GlobalConf ().path ('panda.music-volume').value 
        self._music = loader.loadSfx (file)
        self._music.setLoop (True)
        self.tasks.add (task.sequence (
            task.linear (self._music.setVolume, 0.0, volume, init = True)))
        self._music.play ()

