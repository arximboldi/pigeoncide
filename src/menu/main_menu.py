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

from direct.gui.DirectGui import *

from core import task

from option_menu import *

class MainMenu (object):

    def __init__ (self, state = None, type = None, *a, **k):
        super (MainMenu, self).__init__ (*a, **k)
        if type:
            self.type = type
        if state:
            self.state = state
        self.options_menu = OptionsMenu (state = self.state)
    
    def do_paint (self):
        if self.type == 'main':
            variable_txt = "Start"
        if self.type == 'ingame':
            variable_txt = "Resume"
            
        # Main-Buttons inicialitation
        self.start = DirectButton(geom = self.state.bt_red,
            geom_scale = (4.5, 2, 2),
            geom_pos = (.2, 0, 0.3),
            text = variable_txt,
            text_font = self.state.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.4, 0, 0.8),
            relief = None
            )
        
        self.options = DirectButton(geom = self.state.bt_red,
            geom_scale = (5.7, 2, 2.1),
            geom_pos = (0.2, 0, 0.3),
            text = "Options",
            text_font = self.state.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.1, 0, 0.55),
            relief = None
            ) 

        self.credits = DirectButton(geom = self.state.bt_red,
            geom_scale = (5, 2, 2.1),
            geom_pos = (0.2, 0, 0.3),
            text = "Credits",
            text_font = self.state.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (0, 0, 0.3),
            relief = None
            ) 
        
        self.exit = DirectButton(geom = self.state.bt_red,
            geom_scale = (4, 2, 2),
            geom_pos = (0.2, 0, 0.3),
            text = "Exit",
            text_font = self.state.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (0, 0, 0.05),
            relief = None
            ) 
        
    
    def do_connect (self):
        # Buttons task assigment
        if self.type == 'main':
            self.start["command"] = lambda: self.state.tasks.add( task.sequence(
                self.options_menu.do_destroy (),
                self.state.do_smile (5),
                task.wait (1),
                task.run (lambda: self.state.manager.leave_state ('game'))
            ))
            self.exit["command"] = lambda: self.state.tasks.add (task.sequence(
                task.parallel(
                    self.options_menu.do_destroy (),
                    self.state.do_smile (1.5)
                ),
                task.run (self.state.manager.leave_state)
            ))
        if self.type == 'ingame':
            self.start["command"] = lambda: self.state.tasks.add( task.sequence(
                self.options_menu.do_destroy (),
                self.state.do_smile (5),
                task.wait (1),
                task.run (lambda: self.state.manager.leave_state ('game'))
            ))
            self.exit["command"] = lambda: self.state.tasks.add (task.sequence(
                task.parallel(
                    self.options_menu.do_destroy (),
                    self.state.do_smile (1.5)
                ),
                task.run (self.state.manager.leave_state ('menu'))
            ))            

        self.options["command"] = lambda: self.state.tasks.add (task.sequence (
            task.run (lambda: self.options.setProp ('state', DGG.DISABLED)),
            task.parallel(
                self.state.do_smile (),
                self.show_options ()
            ),
            task.run (lambda: self.options.setProp ('state', DGG.NORMAL))
            ))
            
        self.exit["command"] = lambda: self.state.tasks.add (task.sequence(
            task.parallel(
                self.options_menu.do_destroy (),
                self.state.do_smile (1.5)
            ),
            task.run (self.state.manager.leave_state)
        ))
        
    def do_enable (self):
        self.start.setProp ('state', DGG.NORMAL)
        self.options.setProp ('state', DGG.NORMAL)
        self.credits.setProp ('state', DGG.NORMAL)
        self.exit.setProp ('state', DGG.NORMAL)
        self.options_menu.do_enable ()
    
    def do_disable (self):
        self.start.setProp ('state', DGG.DISABLED)
        self.options.setProp ('state', DGG.DISABLED)
        self.credits.setProp ('state', DGG.DISABLED)
        self.exit.setProp ('state', DGG.DISABLED)
        self.options_menu.do_disable ()
        
    def do_destroy (self):
        self.start.destroy()
        self.options.destroy()
        self.credits.destroy()
        self.exit.destroy()

    def show_options (self):
        if not self.options_menu.active:
            self.move_task = self.options_menu.do_paint ()
            self.options_menu.do_connect ()
        else:
            self.move_task = self.options_menu.do_destroy ()
            
        return self.move_task
    