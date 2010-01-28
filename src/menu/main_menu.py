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

from direct.gui.DirectButton import DirectButton

from basic import BasicMenu
from option_menu import OptionsMenu
from core import task

class MainMenu (object):

    def __init__ (self, state = None, *a, **k):
        super (MainMenu, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.options_menu = OptionsMenu (state = self.state)
    
    def do_paint (self):
        self.bt_red = loader.loadModel ('../data/menu/bt_red.egg')
        self.font = loader.loadFont ('../data/font/three-hours.ttf')
        # Main-Buttons inicialitation
        self.start = DirectButton(geom = self.bt_red,
            geom_scale = (4.5, 2, 2),
            geom_pos = (.2, 0, 0.3),
            text = "Start",
            text_font = self.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.4, 0, 0.8),
            relief = None
            )
        
        self.options = DirectButton(geom = self.bt_red,
            geom_scale = (5.7, 2, 2.1),
            geom_pos = (0.2, 0, 0.3),
            text = "Options",
            text_font = self.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.1, 0, 0.55),
            relief = None
            ) 


        self.credits = DirectButton(geom = self.bt_red,
            geom_scale = (5, 2, 2.1),
            geom_pos = (0.2, 0, 0.3),
            text = "Credits",
            text_font = self.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (0, 0, 0.3),
            relief = None
            ) 
        
        self.exit = DirectButton(geom = self.bt_red,
            geom_scale = (4,2,2),
            geom_pos = (0.2, 0, 0.3),
            text = "Exit",
            text_font = self.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0, 0, 0.05),
            relief = None
            ) 
      
    
    def do_connect (self):
        # Buttons task assigment
        self.start["command"] = lambda: self.state.tasks.add( task.sequence(
            task.run (self.options_menu.do_destroy),
            task.run (lambda: self.state.do_smile (1)),
            task.wait (1),
            task.run (lambda: self.state.manager.change_state ('game'))
        ))
        self.options["command"] = lambda: self.state.tasks.add( task.parallel(
            task.run (self.state.do_smile),
            task.run (self.show_options)
        ))
        self.exit["command"] = self.state.kill
    
    def do_destroy (self):
        self.start.destroy()
        self.options.destroy()
        self.credits.destroy()
        self.exit.destroy()

    def show_options (self):
        if not self.options_menu.active:
            self.options_menu.do_paint ()
            self.options_menu.do_connect ()
        else:
            self.options_menu.do_destroy ()