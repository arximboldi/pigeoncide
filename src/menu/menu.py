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

from pandac.PandaModules import (Vec3, PandaNode, WindowProperties, FontPool)

from core.state import State
#from core.panda_controller import PandaController
from core import task

from main_menu import *
from game.loader import *

class Menu (State):

    def do_setup (self, data):
        props = WindowProperties()
        base.win.requestProperties(props)
        base.setBackgroundColor( 1.0, 1.0, 1.0)
        
        self.root = render.attachNewNode (PandaNode ('menu'))
        self.events.event ('panda-escape').connect (self.kill)
        self.manager.panda.absolute_mouse ()
        
        #Menu setup
        self.setup_camera ()
        self.load_background ()
        self.load_sound ()
        self.load_buttons ()
        self.load_fonts ()
        
        self.main_menu = MainMenu (state = self)
        self.main_menu.do_paint ()
        self.main_menu.do_connect ()

    def do_release (self):
        self.sound.stop ()
        self.main_menu.do_destroy ()
        self.root.removeNode ()
    
    def setup_camera(self):
        camera.setPosHpr( Vec3( 0.0, -22.0, 0.0), Vec3( 0.0, 0.0, 0 ) )
        
    def load_background(self):
        self.bg_normal = loader.loadModel( 'menu/bg_normal.egg' )
        self.bg_normal.reparentTo ( self.root )
        self.bg_normal.setPosHprScale( Vec3( -4.33, 0, -0.89 ), 
            Vec3( 0, 0, 0 ), 
            Vec3( 1748./2480 *10, 9, 10) 
            )
            
        self.bg_smile = loader.loadModel( 'menu/bg_smile.egg' )
        self.bg_smile.reparentTo( self.root )
        self.bg_smile.setPosHprScale( Vec3( -4.33, 1, -0.89 ), 
            Vec3( 0, 0, 0 ), 
            Vec3( 1748./2480 *10, 9, 10) 
            )

    def load_sound (self):
        self.sound = loader.loadSfx ('snd/melancolik-drone.ogg')
        self.sound.setVolume (.1)
        self.sound.setLoop (True)
        self.sound.play ()    
    
    def load_buttons (self):
        self.bt_yellow = loader.loadModel ('menu/bt_yellow.egg')
        self.bt_red = loader.loadModel ('menu/bt_red.egg')

    def load_fonts (self):
        self.font = loader.loadFont ('font/three-hours.ttf')
        
    def do_smile (self, time = 0.2):
        self.tasks.add ( task.sequence(
            task.run (lambda: self.bg_smile.setPos (-4.33, 0 , -0.89)),
            task.run (lambda: self.bg_normal.setPos (-4.33, 1 , -0.89)),
            task.wait (time),
            task.run (lambda: self.bg_normal.setPos (-4.33, 0 , -0.89)),
            task.run (lambda: self.bg_smile.setPos (-4.33, 1 , -0.89))
            ))
        
class MenuData (LoaderData):
    load_models =   [ 'menu/bg_normal.egg',
                      'menu/bg_smile.egg',
                      'menu/bt_red.egg',
                      'menu/bt_yellow.egg'
                    ]
    load_sound  =   [ 'snd/melancolik-drone.ogg' ]
    load_fonts  =   [ 'font/three-hours.ttf' ]
    
class LoadMenu (LoaderInterState):
    load_data = MenuData
    next_state = Menu