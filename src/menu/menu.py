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

class Menu (State):

    def do_setup (self):
        props = WindowProperties()
        props.setCursorHidden(False)
        base.win.requestProperties(props)
        base.setBackgroundColor( 1.0, 1.0, 1.0)

        self.events.event ('panda-escape').connect (self.kill)
        
        #Menu setup
        self.setup_camera ()
        self.load_background ()
        
        self.main_menu = MainMenu (tasks = self.tasks, manager = self.manager)
        self.main_menu.do_paint ()
        self.main_menu.do_connect ()

    def do_update (self, timer):
        pass

    def do_release (self):
        self.main_menu.do_destroy ()
    
    def setup_camera( self ):
        camera.setPosHpr( Vec3( 0.0, -22.0, 0.0), Vec3( 0.0, 0.0, 0 ) )
        
    def load_background( self ):
        self.splashScreen = loader.loadModel( '../data/mesh/background.egg' )
        self.splashScreen.reparentTo( render )
        self.splashScreen.setPosHprScale( Vec3( -4.33, 0, -0.89 ), 
            Vec3( 0, 0, 0 ), 
            Vec3( 420./595 *10, 9, 10) 
            )

