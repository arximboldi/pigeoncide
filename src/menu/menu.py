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

from core.state import State
from pandac.PandaModules import (
    Vec3,
    WindowProperties
)

from main_menu import MainMenu
from pandac.PandaModules import WindowProperties
from core.panda_controller import PandaController
from core import task

class Menu (State):

    def do_setup (self):
        props = WindowProperties()
        base.win.requestProperties(props)
        base.setBackgroundColor( 1.0, 1.0, 1.0)

        self.events.event ('panda-escape').connect (self.kill)
        self.manager.panda.show_mouse ()
        
        #Menu setup
        self.setup_camera ()
        self.load_background ()
        
        self.main_menu = MainMenu (state = self)
        self.main_menu.do_paint ()
        self.main_menu.do_connect ()

    def do_release (self):
        self.main_menu.do_destroy ()
    
    def setup_camera(self):
        camera.setPosHpr( Vec3( 0.0, -22.0, 0.0), Vec3( 0.0, 0.0, 0 ) )
        
    def load_background(self):
        self.bg_normal = loader.loadModel( '../data/menu/bg_normal.egg' )
        self.bg_normal.reparentTo( render )
        self.bg_normal.setPosHprScale( Vec3( -4.33, 0, -0.89 ), 
            Vec3( 0, 0, 0 ), 
            Vec3( 1748./2480 *10, 9, 10) 
            )
        self.bg_smile = loader.loadModel( '../data/menu/bg_smile.egg' )
        self.bg_smile.reparentTo( render )
        self.bg_smile.setPosHprScale( Vec3( -4.33, 1, -0.89 ), 
            Vec3( 0, 0, 0 ), 
            Vec3( 1748./2480 *10, 9, 10) 
            )

    def do_smile (self, time = 0.2):
        self.tasks.add ( task.sequence(
            task.run (lambda: self.bg_smile.setPos (-4.33, 0 , -0.89)),
            task.run (lambda: self.bg_normal.setPos (-4.33, 1 , -0.89)),
            task.wait (time),
            task.run (lambda: self.bg_normal.setPos (-4.33, 0 , -0.89)),
            task.run (lambda: self.bg_smile.setPos (-4.33, 1 , -0.89))
            ))
        
