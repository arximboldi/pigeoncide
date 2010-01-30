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
from direct.gui.OnscreenText import OnscreenText 
from pandac.PandaModules import *

from core import (patch_messenger, task)
#from core import task
from core.panda_controller import PandaController
from base.conf import GlobalConf
#from base.xml_conf import *

class OptionsMenu (object):

    def __init__ (self, state = None, *a, **k):
        super (OptionsMenu, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False
        self.sub_screen = Screen(state)
        self.sub_sound = Sound (state)
        self.sub_keyboard = Keyboard (state)
        
        self.cfg = GlobalConf().child ('panda')

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
        self.sound ["command"] = self.show_sound
        self.keyboard ["command"] = self.show_keyboard
        self.screen ["command"] = self.show_screen
        self.back ["command"] = lambda: self.state.tasks.add (self.do_destroy())
        
    def do_destroy (self):
        if self.active:
            #Buttons destroy
            self.sound.setProp ('state',DGG.DISABLED)
            self.keyboard.setProp ('state',DGG.DISABLED)
            self.screen.setProp ('state',DGG.DISABLED)
            self.back.setProp ('state',DGG.DISABLED)

            #Movement task creation
            self.move_task = task.sequence (
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
                            
            if self.sub_screen.active:
                self.sub_screen.do_destroy ()
                            
            if self.sub_sound.active:
                self.sub_sound.do_destroy ()
                
            if self.sub_keyboard.active:
                self.sub_keyboard.do_destroy ()
                
            #The option_menu is set as inactive 
            self.active = False

            return self.move_task

    def show_sound (self):
        if not self.sub_sound.active:
            self.sub_sound.do_paint ()
        else:
            self.sub_sound.do_destroy ()
    
    def show_screen (self):
        if not self.sub_screen.active:
            self.sub_screen.do_paint ()
        else:
            self.sub_screen.do_destroy ()
            
        pass
        
    def show_keyboard (self):
        if not self.sub_keyboard.active:
            self.sub_keyboard.do_paint ()
        else:
            self.sub_keyboard.do_destroy ()
    
class Keyboard (object):

    def __init__(self, state = None, *a, **k):
        super (Keyboard, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False
        
    def do_paint (self):
        #cfg.child ('music-volume').default (self.DEFAULT_MUSIC_VOLUME)
        self.active = True

    def do_destroy (self):
        self.active = False

    def get_active (self):
        return self.active

class Sound (object):

    def __init__(self, state = None, *a, **k):
        super (Sound, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False
        self.cfg = GlobalConf().child ('panda')
        
            
    def do_paint (self):
        #
        # TO DO:    - Place the sliders and label in correct place. 
        #           - Test colors and style 
        #
        
        self.active = True
        
        # Creates volume label and slider
        self.vol_lab = OnscreenText(text = 'SFX',
            font = self.state.font,
            pos = (-0.5, 0.02),
            scale = 0.07,
            )
        self.vol_slider = DirectSlider(range=(0, 1),
            value = self.cfg.child ('sound-volume').value,
            pageSize = 0.03,
            command = self.change_snd,
            pos = (-0.1, 0, 0.55),
            )

        # Creates music label and slider
        self.mus_lab = OnscreenText(text = 'Music',
            font = self.state.font,
            pos = (-0.5, 0.02),
            scale = 0.07
            )
        self.mus_slider = DirectSlider(range=(0, 1),
            value = self.cfg.child ('music-volume').value,
            pageSize = 0.03,
            command = self.change_snd
            )

    def do_destroy (self):
        self.mus_lab.destroy ()
        self.mus_slider.destroy ()
        self.vol_lab.destroy ()
        self.vol_slider.destroy ()
        self.active = False

    def change_snd (self):
        # Modifies config acording to sliders values
        self.cfg.child ('sound-volume').set_value (self.vol_slider['value']) 
        self.cfg.child ('music-volume').set_value (self.mus_slider['value'])

class Screen (object):

    def __init__(self, state = None, *a, **k):
        super (Screen, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False
        self.cfg = GlobalConf().child ('panda')
        
    def do_paint (self):
        # Get possible screen resolutions NOT AVAILABLE IN OSX
        # di = base.pipe.getDisplayInformation()
        # for index in range(di.getTotalDisplayModes()): 
        #    sizes += (  str(di.getDisplayModeWidth(index)), 
        #                str(di.getDisplayModeHeight(index))
        #            )         
        
        actual_full = self.cfg.child ('fullscreen').value
        actual_width = self.cfg.child ('width').value
        actual_height = self.cfg.child ('height').value
        self.active = True
        
        self.sizes = [  [640, 480],
                        [800, 600],
                        [1024, 768],
                        [1280, 800],
                        [1280, 1024],
                        [1440, 900]
                        ]

        self.sizes_tx = []
        for a in self.sizes:
            self.sizes_tx += [str (a[0])+"x"+str (a[1])]
        
        # Gets the position of the actual config from self.sizes
        init_item = self.sizes.index ([actual_width, actual_height])

        #
        # TO DO: place buttons in correct positions and FPS button
        #
        # cfg.child ('fps').default (self.DEFAULT_FPS)
        # cfg.child ('frame-meter').default (self.DEFAULT_FRAME_METER)
            
        # Create a frame
        self.res_menu = DirectOptionMenu (text="Resolution", 
            scale = 0.1,
            items = self.sizes_tx,
            initialitem = init_item,
            highlightColor = (0.65,0.65,0.65,1),
            command = self.change_res
            )
        
        self.full_screen = DirectCheckButton (text = "Full screen" ,
            indicatorValue = self.cfg.child ('fullscreen').get_value(),            pos = (.4, 0, -.5),
            scale = .05,
            command = self.change_full
            )
    
    def do_destroy (self):
        self.res_menu.destroy ()
        self.full_screen.destroy ()
        self.active = False
        
    def get_active (self):
        return self.active
        
    def change_full (self, status):
        self.cfg.child ('fullscreen').set_value (status)
        self.cfg.nudge ()
        
    def change_res (self, arg):
        i = self.sizes_tx.index(arg)
        self.cfg.child ('fullscreen').set_value (False)
        self.cfg.child ('width').set_value (self.sizes[i][0])
        self.cfg.child ('height').set_value (self.sizes[i][1])

        self.full_screen["indicatorValue"] = False
        self.cfg.nudge ()