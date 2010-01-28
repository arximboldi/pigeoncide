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
from core import task

class OptionsMenu (object):

    def __init__ (self, state = None, *a, **k):
        super (OptionsMenu, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False

    def do_paint (self):
        self.bt_yellow = loader.loadModel ('../data/menu/bt_yellow.egg')
        self.font = loader.loadFont ('../data/font/three-hours.ttf')

        # Option-Buttons inicialitation
        self.sound = DirectButton(geom = self.bt_yellow,
            geom_scale = (4.5, 2, 2),
            geom_pos = (.4, 0, 0.3),
            text = "Sound",
            text_font = self.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.1, 0, 0.55),
            relief = None
            )

        self.keyboard = DirectButton(geom = self.bt_yellow,
            geom_scale = (6.8, 2, 2.2),
            geom_pos = (.6, 0, 0.3),
            text = "Keyboard",
            text_font = self.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.1, 0, 0.55),
            relief = None
            )
            
        self.screen = DirectButton(geom = self.bt_yellow,
            geom_scale = (4.7, 2, 2),
            geom_pos = (.4, 0, 0.3),
            text = "Screen",
            text_font = self.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.1, 0, 0.55),
            relief = None
            )
            
        self.back = DirectButton(geom = self.bt_yellow,
            geom_scale = (4, 2, 2),
            geom_pos = (.4, 0, 0.3),
            text = "Back",
            text_font = self.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.1, 0, 0.55),
            relief = None
            )

        self.state.tasks.add (task.parallel(
            task.sinusoid (lambda x: self.sound.setPos (x * 0.3, 2-x, .45)),
            task.sinusoid (lambda x: self.sound.setAlphaScale (x))
            ))
            
        self.state.tasks.add (task.parallel(
            task.sinusoid (lambda x: 
                self.keyboard.setPos ((x*0.45)-0.1, 1-x,(x*-0.25)+0.45)),
            task.sinusoid (lambda x: self.keyboard.setAlphaScale (x))
        ))
        
        self.state.tasks.add (task.parallel (
            task.sinusoid (
                lambda x: self.screen.setPos ((x*0.4)-0.1, 1-x,(x*-0.50)+0.45)),
            task.sinusoid (lambda x: self.screen.setAlphaScale (x))
        ))
        
        self.state.tasks.add (task.parallel(
            task.sinusoid (
                lambda x: self.back.setPos ((x*0.35)-0.1, 1-x,(x*-0.75)+0.45)),
            task.sinusoid (lambda x: self.back.setAlphaScale (x))
        ))
            
        self.active = True
            
    def do_connect (self):
        # Buttons task assigment
        self.sound ["command"] = lambda: self.do_paint_sound ()
        self.keyboard ["command"] = lambda: self.do_paint_keyboard ()
        self.screen ["command"] = lambda: self.do_paint_screen ()
        self.back ["command"] = lambda: self.do_destroy ()
        
    def do_destroy (self):
        if self.active:
            #Each task moves the button back to the "option" button changing
            #its alpha too.
            self.state.tasks.add (task.parallel(
                task.sequence (task.sinusoid (lambda x: 
                    self.sound.setPos ((x*-0.4)+0.3, 0, .45)),
                    task.run (self.sound.destroy)
                ),
                task.sinusoid (lambda x: self.sound.setAlphaScale (1-x))
            ))
            
            self.state.tasks.add (task.parallel (
                task.sequence (task.sinusoid (lambda x: 
                    self.keyboard.setPos ((x*-0.45)+0.35,0,(x*0.25)+0.2)), 
                    task.run (self.keyboard.destroy)
                ),
                task.sinusoid (lambda x: self.keyboard.setAlphaScale (1-x))
            ))
            
        
            self.state.tasks.add (task.parallel (
                task.sequence (task.sinusoid (lambda x: 
                    self.screen.setPos ((x*-0.4)+0.3, 0,(x*0.50)-0.05)),
                    task.run (self.screen.destroy)
                ),
                task.sinusoid (lambda x: self.screen.setAlphaScale (1-x))
            ))

            self.state.tasks.add (task.parallel (
                task.sequence (task.sinusoid (lambda x: 
                    self.back.setPos ((x*-0.35)+0.25, 0,(x*0.75)-0.30)),
                    task.run (self.back.destroy)
                ),
                task.sinusoid (lambda x: self.back.setAlphaScale (1-x))
            ))
                    
            self.active = False

            
    def do_paint_sound (self):
        pass
    
    def do_paint_keyboard (self):
        pass
        
    def do_paint_screen (self):
        pass

