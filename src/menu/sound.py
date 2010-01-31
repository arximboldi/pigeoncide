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


from base.conf import GlobalConf
from core.input import *

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
        scale = 0.4
        y = -0.4
        
        # Creates volume label and slider
        self.vol_lab = OnscreenText(text = 'SFX',
            font = self.state.font,
            pos = (0, y-0.02),
            scale = 0.07,
            )
        self.vol_slider = DirectSlider(range=(0, 1),
            value = self.cfg.child ('sound-volume').value,
            pageSize = 0.03,
            command = self.change_snd,
            scale = scale,
            pos = (0.6, 0, y)
            )

        # Creates music label and slider
        self.mus_lab = OnscreenText(text = 'Music',
            font = self.state.font,
            pos = (0, y-0.22),
            scale = 0.07
            )
        self.mus_slider = DirectSlider(range=(0, 1),
            value = self.cfg.child ('music-volume').value,
            pageSize = 0.03,
            command = self.change_snd,
            scale = scale,
            pos = (0.6, 0, y-0.2)
            )
        #self.mus_slider.setPos (0.3, 0, -0.4)

    def do_enable (self):
        pass
        
    def do_disable (self):
        pass
        
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

