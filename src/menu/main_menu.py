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

from basic import BasicMenu
from option_menu import OptionsMenu
from core import task

class MainMenu (BasicMenu):

    def __init__ (self, *a, **k):
        super (MainMenu, self).__init__ (*a, **k)
        self.options_menu = OptionsMenu (state = self.state)
    
    def do_paint (self):
        # Main-Buttons inicialitation
        self.start = self.create_button ("Start", pos = (-0.3, 0.7))
        # self.tasks.add (task.sinusoid (
        #     lambda x: self.start.setPos (x, 0, .45)))
        
        self.options = self.create_button ("Options", pos = (-0.1, 0.45))
        #self.tasks.add (task.sinusoid (
        #    lambda x: self.options.setPos (x, 0, .45)))
            
        self.credits = self.create_button ("Credits", pos = (0, 0.2))
        self.exit = self.create_button ("Exit", pos = (-0.1, -0.05))        
    
    def do_connect (self):
        # Buttons task assigment
        self.start["command"] = lambda: self.state.tasks.add( task.sequence(
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