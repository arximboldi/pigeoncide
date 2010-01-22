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
from core import task

class OptionsMenu (BasicMenu):

    def __init__ (self, state = None, *a, **k):
        super (BasicMenu, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False

    def do_paint (self):
        # Option-Buttons inicialitation
        self.sound = self.create_button ("Sound", pos = (-0.1, 0.45))
        
        self.state.tasks.add (task.sinusoid (
            lambda x: self.sound.setPos (x * 0.3, 0, .45)))
            
        self.keyboard = self.create_button ("Keyboard", pos = (-0.1, 0.45))
        self.state.tasks.add (task.sinusoid (
            lambda x: self.keyboard.setPos ((x*0.45)-0.1, 0,(x*-0.25)+0.45)))
            
        self.screen = self.create_button ("Screen", pos = (-0.1, 0.45))
        self.state.tasks.add (task.sinusoid (
            lambda x: self.screen.setPos ((x*0.4)-0.1, 0,(x*-0.50)+0.45)))
            
        self.back = self.create_button ("Back", pos = (-0.1 , 0.45))
        self.state.tasks.add (task.sinusoid (
            lambda x: self.back.setPos ((x*0.35)-0.1, 0,(x*-0.75)+0.45)))
            
        self.active = True
            
    def do_connect (self):
        # Buttons task assigment
        self.sound ["command"] = lambda: self.do_paint_sound ()
        self.keyboard ["command"] = lambda: self.do_paint_keyboard ()
        self.screen ["command"] = lambda: self.do_paint_screen ()
        self.back ["command"] = lambda: self.do_destroy ()
        
    def do_destroy (self):        
        self.state.tasks.add (task.sequence (
            task.sinusoid (lambda x: self.sound.setPos ((x*-0.4)+0.3, 0, .45)),
            task.run (self.sound.destroy)
            ))
            
        self.state.tasks.add (task.sequence (
            task.sinusoid (lambda x: self.keyboard.setPos ((x*-0.45)+0.35, 0,(x*0.25)+0.2)),
            task.run (self.keyboard.destroy)
            ))
            
        
        self.state.tasks.add (task.sequence (
            task.sinusoid (lambda x: self.screen.setPos ((x*-0.4)+0.3, 0,(x*0.50)-0.05)),
            task.run (self.screen.destroy)
            ))

        self.state.tasks.add (task.sequence (
            task.sinusoid (lambda x: self.back.setPos ((x*-0.35)+0.25, 0,(x*0.75)-0.30)),
            task.run (self.back.destroy)
            ))
                    
        self.active = False

            
    def do_paint_sound (self):
        pass
    
    def do_paint_keyboard (self):
        pass
        
    def do_paint_screen (self):
        pass

