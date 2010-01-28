#
#  Copyright (C) 2010 Juan Pedro Bolivar Puente, Alberto Villegas Erce
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

from core import task
from core.state import State
from ent.game import LightGameState
import ui

class LoaderInterState (State):

    data        = None
    next_state  = None
    next_args   = []
    next_kwargs = {}
    
    def do_setup (self, data = None):
        if data:
            self.data = data
        self.manager.enter_state (LoaderState, self.data)

    def do_unsink (self):
        self.manager.change_state (self.next_state,
                                   self.data,
                                   *self.next_args,
                                   **self.next_kwargs)

class LoaderData (object):

    models   = []
    textures = []
    fonts    = []
    sounds   = []
    
    def __init__ (self,
                  models   = None,
                  textures = None,
                  fonts    = None,
                  sounds   = None,
                  *a, **k):
        super (LoaderData, self).__init__ (*a, **k)

        if models:   self.models   = models
        if textures: self.textures = textures
        if fonts:    self.fonts    = fonts
        if sounds:   self.sounds   = sounds


class LoaderState (LightGameState):
    
    def do_setup (self, data):
        self.manager.panda.set_background_color (0, 0, 0)

        self._data = data
        self._text = ui.TextEntity (entities = self.entities,
                                    font = 'font/gilles.ttf',
                                    text = "Loading ... 0%",
                                    fg   = (1, 1, 1, 1))

        self._num_things = len (data.load_models)   + \
                           len (data.load_textures) + \
                           len (data.load_fonts)    + \
                           len (data.load_sounds)
        self._done_things = 0

        self._curr_iter  = iter (data.load_models)
        self._curr_thing = 0
        
        self._loaders  = [ loader.loadModel,
                           loader.loadTexture,
                           loader.loadFont,
                           loader.loadSfx ]
        self._things   = [ data.load_models,
                           data.load_textures,
                           data.load_fonts,
                           data.load_sounds ]

        self._init = False

        self._text.alpha = 1.0
        self.tasks.add (self.loader_task)
        
    def loader_task (self, timer):
        if not self._init:
            self._init = True
        try:
            item = self._curr_iter.next ()
            self._loaders [self._curr_thing] (item)
            self._done_things += 1
            self._text.text = "Loading ... %i%%" % (
                100 * self._done_things / self._num_things)
            
        except StopIteration, e:
            self._curr_thing += 1
            if self._curr_thing < len (self._loaders):
                self._curr_iter = iter (self._things [self._curr_thing])
            else:
                self._text.fade_out ().add_next (task.run (self.kill))
                return task.killed
        
        return task.running
