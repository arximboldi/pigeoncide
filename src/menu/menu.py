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

from pandac.PandaModules import (Vec3, 
    PandaNode, 
    WindowProperties, 
    FontPool,
    Texture)

from base.log import get_log
from core.state import State
#from core.panda_controller import PandaController
from core import task

from main_menu import *
from game.loader import *

_log = get_log (__name__)

class Menu (State):

    def __del__ (self):
        _log.debug ("Releasing the menu from memory.")

    def do_setup (self, data, type = 'main'):
        self.type = type
        self.root = base.cam.attachNewNode (PandaNode ('menu'))
        self.events.event ('panda-escape').connect (self.manager.leave_state)
        self.manager.panda.absolute_mouse ()
        
        #Menu setup
        self.setup_camera ()
        self.load_background ()
        self.load_sound ()
        self.load_buttons ()
        self.load_fonts ()
        
        #Load game defaults
        load_game_defaults ()
        
        #Load and show main menu
        self.main_menu = MainMenu (state = self, type = self.type)
        self.main_menu.do_paint ()
        self.main_menu.do_connect ()

    def do_release (self):
        self.main_menu.do_destroy ()
        self.root.removeNode ()
        
    def setup_camera(self):
        #camera.setPosHpr( Vec3( 0.0, -22.0, 0.0), Vec3( 0.0, 0.0, 0 ) )
        pass
    
    def load_background(self):
        bp = Vec3( 0.0, -22.0, 0.0)
        pos = Vec3 (-4.33, 0, -0.89) - bp
        
        self.bg_normal = loader.loadModel( 'menu/bg_normal.egg' )
        self.bg_normal.reparentTo ( self.root )
        self.bg_normal.setPosHprScale (pos, 
            Vec3 (0, 0, 0), 
            Vec3 (1748./2480 *10, 1, 10) 
            )
            
        self.bg_smile = loader.loadModel ('menu/bg_smile.egg')
        #self.bg_smile.reparentTo (self.root)
        self.bg_smile.setPosHprScale (pos, 
            Vec3 (0, 0, 0), 
            Vec3 (1748./2480 *10, 1, 10) 
            )
        
    def load_sound (self):
        self.manager.panda.loop_music ('snd/melancolik-drone.ogg')
    
    def load_buttons (self):
        self.bt_yellow = loader.loadModel ('menu/bt_yellow.egg')
        self.bt_red = loader.loadModel ('menu/bt_red.egg')

    def load_fonts (self):
        self.font = loader.loadFont ('font/three-hours2.ttf')

    def to_smile (self):
        self.bg_smile.reparentTo (self.root)
        self.bg_normal.detachNode ()

    def to_normal (self):
        self.bg_normal.reparentTo (self.root)
        self.bg_smile.detachNode ()
    
    def do_smile (self, time = 0.2):
        return task.sequence(
            task.run (self.to_smile),
            task.wait (time),
            task.run (self.to_normal))
    
    def do_enable (self):
        self.main_menu.do_enable ()
        
    def do_disable (self):
        self.main_menu.do_disable ()
        
class MenuData (LoaderData):
    load_models =   [ 'menu/bg_normal.egg',
                      'menu/bg_smile.egg',
                      'menu/bt_red.egg',
                      'menu/bt_yellow.egg'
                    ]
    load_sound  =   [ 'snd/melancolik-drone.ogg' ]
    load_fonts  =   [ 'font/three-hours2.ttf' ]
    
class LoadMenu (LoaderInterState):
    load_data = MenuData
    next_state = Menu
