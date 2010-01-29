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

class OptionsMenu (object):

    def __init__ (self, state = None, *a, **k):
        super (OptionsMenu, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False

    def do_paint (self):
        # Option-Buttons inicialitation
        self.sound = DirectButton(geom = self.state.bt_yellow,
            geom_scale = (4.5, 2, 2),
            geom_pos = (.4, 0, 0.3),
            text = "Sound",
            text_font = self.state.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.1, 0, 0.55),
            relief = None,
            state = DGG.DISABLED
            )
        self.sound.setAlphaScale (0)

        self.keyboard = DirectButton(geom = self.state.bt_yellow,
            geom_scale = (6.8, 2, 2.2),
            geom_pos = (.6, 0, 0.3),
            text = "Keyboard",
            text_font = self.state.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.1, 0, 0.55),
            relief = None,
            state = DGG.DISABLED
            )
        self.keyboard.setAlphaScale (0)
                    
        self.screen = DirectButton(geom = self.state.bt_yellow,
            geom_scale = (4.7, 2, 2),
            geom_pos = (.4, 0, 0.3),
            text = "Screen",
            text_font = self.state.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.1, 0, 0.55),
            relief = None,
            state = DGG.DISABLED
            )
        self.screen.setAlphaScale (0)
                    
        self.back = DirectButton(geom = self.state.bt_yellow,
            geom_scale = (4, 2, 2),
            geom_pos = (.4, 0, 0.3),
            text = "Back",
            text_font = self.state.font,
            text_scale = (0.8, 0.9),
            scale = .1,
            pos = (-0.1, 0, 0.55),
            relief = None,
            state = DGG.DISABLED
            )
        self.back.setAlphaScale (0)
        
        #Movement task creation
        self.move_task = task.sequence(
            task.parallel(
                task.sinusoid (lambda x: 
                    self.sound.setPos ((x*0.55)-0.1, 0, 0.55+(x*0.25))),
                task.sinusoid (lambda x: self.sound.setAlphaScale (x)),
                
                task.sinusoid (lambda x: 
                    self.keyboard.setPos ((x*0.7)-0.1, 0, 0.55)),
                task.sinusoid (lambda x: self.keyboard.setAlphaScale (x)),

                task.sinusoid (lambda x: 
                    self.screen.setPos ((x*0.65)-0.1, 0, 0.55-(x*0.25))),
                task.sinusoid (lambda x: self.screen.setAlphaScale (x)),

                task.sinusoid (lambda x:
                    self.back.setPos ((x*0.65)-0.1, 0, 0.55-(x*0.5))),
                task.sinusoid (lambda x: self.back.setAlphaScale (x))
            ),
            task.run (lambda: self.sound.setProp('state',DGG.NORMAL)),
            task.run (lambda: self.keyboard.setProp('state',DGG.NORMAL)),
            task.run (lambda: self.screen.setProp('state',DGG.NORMAL)),
            task.run (lambda: self.back.setProp('state',DGG.NORMAL))
            )
        
        #The option_menu is set as active
        self.active = True
        
        return self.move_task
        
    def do_connect (self):
        # Buttons task assigment
        self.sound ["command"] = lambda: self.do_paint_sound ()
        self.keyboard ["command"] = lambda: self.do_paint_keyboard ()
        self.screen ["command"] = lambda: self.do_paint_screen ()
        self.back ["command"] = lambda: self.state.tasks.add (self.do_destroy())
        
    def do_destroy (self):
        if self.active:
            #Buttons destroy
            self.sound.setProp ('state',DGG.DISABLED)
            self.keyboard.setProp ('state',DGG.DISABLED)
            self.screen.setProp ('state',DGG.DISABLED)
            self.back.setProp ('state',DGG.DISABLED)

            #Movement task creation
            self.move_task = task.sequence(
                task.parallel(
                    task.sinusoid (lambda x: 
                        self.sound.setPos (0.45-(x*0.55), 0, .8-(x*0.25))),
                    task.sinusoid (lambda x: self.sound.setAlphaScale (1-x)),
                    
                    task.sinusoid (lambda x: 
                        self.keyboard.setPos (0.6-(x*0.7), 0, 0.55)),
                    task.sinusoid (lambda x: self.keyboard.setAlphaScale (1-x)),

                    task.sinusoid (lambda x: 
                        self.screen.setPos (0.55-(x*0.65), 0, 0.3+(x*0.25))),
                    task.sinusoid (lambda x: self.screen.setAlphaScale (1-x)),
                    
                    task.sinusoid (lambda x: 
                        self.back.setPos (0.55-(x*0.65), 0, 0.05+(x*0.5))),
                    task.sinusoid (lambda x: self.back.setAlphaScale (1-x))
                ),
                task.run (self.sound.destroy),
                task.run (self.back.destroy),
                task.run (self.keyboard.destroy),
                task.run (self.screen.destroy)
                )
            #The option_menu is set as inactive 
            self.active = False
            
            return self.move_task
            
    def do_paint_sound (self):
        pass
    
    def do_paint_keyboard (self):
        pass
        
    def do_paint_screen (self):
        self.full_screen = DirectCheckButton(text = "Full screen" ,
            pos = (.4, 0, -.5),
            scale=.05,
            #command=setText
            )
        

