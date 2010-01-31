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
        
        self.sizes = [  (640, 480),
                        (800, 600),
                        (1024, 768),
                        (1280, 800),
                        (1280, 1024),
                        (1440, 900)
                        ]

        self.sizes_tx = []
        for h, w in self.sizes:
            self.sizes_tx += [str (h)+"x"+str (w)]
        
        # Gets the position of the actual config from self.sizes
        init_item = self.sizes.index ((actual_width, actual_height))

        #
        # TO DO: place buttons in correct positions
        #
            
        # Create a frame
        tx_scale = (0.7, 0.7)
        self.rest_txt = OnscreenText (text = "Resolution",
            font = self.state.font,
            pos = (0.4, 0, -0.4)
            )
        self.res_menu = DirectOptionMenu (text = "Resolution",
            text_font = self.state.font, 
            text_scale = tx_scale,
            popupMarker_text_font = self.state.font, 
            scale = 0.1,
            items = self.sizes_tx,
            initialitem = init_item,
            highlightColor = (0.65,0.65,0.65,1),
            command = self.change_res,
            pos = (0.6, 0, -0.4)
            )
        
        self.full_screen = DirectCheckButton (text = "Full screen",
            text_font = self.state.font,     
            text_scale = tx_scale,
            indicatorValue = self.cfg.child ('fullscreen').value,
            scale = .08,
            command = self.change_full,
            pos = (0.6, 0, -0.6)
            )
            
        self.fps_display = DirectCheckButton (text = "FPS display",
            text_font = self.state.font,
            text_scale = tx_scale,
            indicatorValue = self.cfg.child ('frame-meter').value,
            scale = .08,
            command = self.change_fps,
            pos = (0.6, 0, -0.8)
            )

    def do_enable (self):
        pass
        
    def do_disable (self):
        pass
        
    def do_destroy (self):
        self.res_menu.destroy ()
        self.fps_display.destroy ()
        self.full_screen.destroy ()
        self.active = False
        
    def change_fps (self, status):
        self.cfg.child ('frame-meter').set_value (status)
        
    def change_full (self, status):
        self.cfg.child ('fullscreen').set_value (status)
        self.cfg.nudge ()
        
    def change_res (self, arg):
        i = self.sizes_tx.index(arg)
        self.cfg.child ('width').set_value (self.sizes[i][0])
        self.cfg.child ('height').set_value (self.sizes[i][1])
        self.cfg.nudge ()