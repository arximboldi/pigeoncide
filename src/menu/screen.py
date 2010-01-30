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
from core.input import *
#from base.xml_conf import *

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
        
        self.full_screen = DirectCheckButton (text = "Full screen",
            indicatorValue = self.cfg.child ('fullscreen').get_value(),
            pos = (.4, 0, -.5),
            scale = .05,
            command = self.change_full
            )
            
        self.fps_display = DirectCheckButton (text = "FPS display",
            indicatorValue = self.cfg.child ('frame-metter').get_value(),
            pos = (.4, 0, -.7),
            scale = .05,
            command = self.change_fps
            )

    def do_enable (self):
        pass
        
    def do_disable (self):
        pass
        
    def do_destroy (self):
        self.res_menu.destroy ()
        self.fps_display ()
        self.full_screen.destroy ()
        self.active = False
        
    def change_fps (self, status):
        self.cfg.child ('frame-metter').set_value (status)
        
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