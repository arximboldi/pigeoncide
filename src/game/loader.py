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

from base.log import get_log
from base.util import linear
from error import GameError
from core import task
from core.state import State
from ent.game import LightGameState
from ent import panda

from pandac.PandaModules import *

import ui
import gc

_log = get_log (__name__)

loader_loading  = 0
loader_running  = 1
loader_cleaning = 2

class LoaderError (GameError): pass

class LoaderInterState (State):

    load_data   = None

    next_state  = None
    next_args   = []
    next_kwargs = {}

    last_state  = None
    last_args   = []
    last_kwargs = {}
    
    def do_setup (self, data = None):
        if data:
            self._data = data
        else:
            self._data = self.load_data
        
        if isinstance (self._data, type):
            self._data = self._data ()
        
        _log.debug ('Loading data for state: ' + str (self.next_state))
        self._data.load_phase = loader_loading
        self.manager.enter_state (LoaderState, self._data)
    
    def do_unsink (self, last_state = None, *last_args, **last_kwargs):
        if self._data.load_phase == loader_loading:
            _log.debug ('Entering state: ' + str (self.next_state))
            self._data.load_phase = loader_running
            self.manager.enter_state (self.next_state,
                                      self._data,
                                      *self.next_args,
                                      **self.next_kwargs)

        elif self._data.load_phase == loader_running:
            if last_state:
                self.last_state  = last_state
                self.last_args   = last_args
                self.last_kwargs = last_kwargs
            _log.debug ('Cleaning data for state: ' + str (self.next_state))
            self._data.load_phase = loader_cleaning
            self.manager.enter_state (CleanerState, self._data)
            
        elif self._data.load_phase == loader_cleaning:
            _log.debug ('Loader finished, entering: ' + str (self.next_state))
            if self.last_state:
                self.manager.change_state (self.last_state,
                                           *self.last_args,
                                           **self.last_kwargs)
            else:
                self.manager.leave_state ()
        else:
            raise LoaderError ('Unknown phase: ' + str (self._data.load_phase))


class LoaderData (object):

    load_models     = []
    load_textures   = []
    load_fonts      = []
    load_sounds     = []
    load_phase      = loader_loading    

    load_increasing   = False
    
    def __init__ (self,
                  models   = None,
                  textures = None,
                  fonts    = None,
                  sounds   = None,
                  *a, **k):
        super (LoaderData, self).__init__ (*a, **k)

        if models:   self.load_models   = models
        if textures: self.load_textures = textures
        if fonts:    self.load_fonts    = fonts
        if sounds:   self.load_sounds   = sounds
        
        self.load_results = [ [], [], [], [] ]


class LoaderState (LightGameState):

    _prg_min_pos      = Vec3 (-2, 0, 0)
    _prg_max_pos      = Vec3 (0.7,  0, 0)
    _red_min_pos      = Vec3 (-3, 0, 0)
    _red_max_pos      = Vec3 (0,  0, 0)
    _blood_color      = Vec3 (227, 30, 38)
    
    def do_setup (self, data):
        self.manager.panda.set_background_color (1, 1, 1)

        self._data  = data

        # TODO: We should cleanup the ui code to avoid this kind of shit.
        camera.setPosHpr (Vec3 (0.0, -22.0, 0.0), Vec3 (0.0, 0.0, 0))
        self._pic_boy = panda.ModelEntity (entities = self.entities,
                                           model = 'menu/bg_smile.egg')
        self._pic_boy.model.setTransparency (TransparencyAttrib.MAlpha)
        self._pic_boy.model_position = Vec3 (-4.33, 0, -0.89)
        self._pic_boy.model_scale    = Vec3 (1748./2480.*10, 1, 10)
        
        self._pic_red = ui.ImageEntity (entities = self.entities,
                                        image = 'hud/red-bg.png')
    
        self._pic_red.position = Vec3 (-3., 0, 0)
        self._pic_prg = ui.ImageEntity (entities = self.entities,
                                        image = 'hud/blood-bg.png')
        self._pic_prg.position = Vec3 (-2, 0, 0)
        
        self._txt_prg = ui.TextEntity (entities = self.entities,
                                       font = 'font/gilles.ttf',
                                       text = "Loading ... 0%")
        
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

        self._txt_prg.alpha = 1.0
        self.tasks.add (self.loader_task)

    def update_progress (self, progress):
        self._txt_prg.text = "Loading ... %i%%" % (int (progress * 100.))
        if not self._data.load_increasing:
            progress = 1. - progress    
        self._pic_prg.position = linear (self._prg_min_pos, self._prg_max_pos,
                                         progress)
        self._pic_red.position = linear (self._red_min_pos, self._red_max_pos,
                                         progress)
        
    def loader_task (self, timer):
        if not self._init:
            self._init = True
        try:
            item = self._curr_iter.next ()
            res = (item, self._loaders [self._curr_thing] (item))
            if res:
                self._data.load_results [self._curr_thing].append (res)
                
            self._done_things += 1
            self.update_progress (float (self._done_things) / self._num_things)
            
        except StopIteration, e:
            self._curr_thing += 1
            if self._curr_thing < len (self._loaders):
                self._curr_iter = iter (self._things [self._curr_thing])
            else:
                self._txt_prg.fade_out ().add_next (task.run (
                    self.manager.leave_state))
                self.manager.panda.set_background_color (
                    * (self._blood_color if self._data.load_increasing else
                       Vec3 (1, 1, 1)))
                return task.killed
        
        return task.running


class CleanerState (State):

    def do_setup (self, data):
        self._cleaners = [ lambda (n, r): loader.unloadModel (r),
                           lambda (n, r): loader.unloadTexture (r),
                           lambda (n, r): FontPool.releaseFont (n),
                           lambda (n, r): loader.unloadSfx (r) ]
        
        for res, cleaner in zip (data.load_results, self._cleaners):
            for r in res:
                cleaner (r)
        self.kill ()
