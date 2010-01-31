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


from base.conf import GlobalConf
from core.input import *
from base.meta import *

@monkeypatch (DirectOptionMenu)
def _unhighlightItem(self, item, frameColor): 
        """ Clear frame color, clear highlightedIndex """ 
        item['frameColor'] = frameColor 
        item['frameSize'] = (self.minX, self.maxX, self.minZ, self.maxZ) 
        item['text_scale'] = self['highlightScale']        
        self.highlightedIndex = None 
        
class Screen (object):

    def __init__(self, state = None, *a, **k):
        super (Screen, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False
        self.cfg_p = GlobalConf().child ('panda')
        self.cfg_g = GlobalConf().child ('game')        
    
    def do_paint (self):
        # Get possible screen resolutions NOT AVAILABLE IN OSX
        # di = base.pipe.getDisplayInformation()
        # for index in range(di.getTotalDisplayModes()): 
        #    sizes += (  str(di.getDisplayModeWidth(index)), 
        #                str(di.getDisplayModeHeight(index))
        #            )         
        
        actual_full = self.cfg_p.child ('fullscreen').value
        actual_width = self.cfg_p.child ('width').value
        actual_height = self.cfg_p.child ('height').value
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
        # TO DO: add images to check buttos
        #
            
        # Create a frame
        tx_scale = (0.9, 0.9)
        self.res_txt = OnscreenText (text = "Resolution",
            font = self.state.font,
            align = TextNode.ALeft,
            pos = (-0.1, -0.4)
            )
        self.res_menu = DirectOptionMenu (text = "Resolution",
            highlightScale = tx_scale,
            text_font = self.state.font, 
            text_scale = tx_scale,
            item_text_font = self.state.font,
            item_text_scale = tx_scale,
            scale = 0.08,
            items = self.sizes_tx,
            initialitem = init_item,
            highlightColor = (0.65,0.65,0.65,1),
            command = self.change_res,
            pos = (0.5, 0, -0.4)
            )
        
        #checked = loader.loadModel ('menu/checked.egg')
        #unchecked = loader.loadModel ('menu/unchecked.egg')
        self.full_screen = DirectCheckButton (text = "Full screen",
            text_font = self.state.font,     
            text_scale = tx_scale,
            #text_pos = (0.5, 0, -0.7),
            text_align = TextNode.ALeft,
            indicatorValue = self.cfg_p.child ('fullscreen').value,
            scale = .08,
            relief = None,
            boxPlacement = 'right',
            boxRelief = None,
            #boxImage = (unchecked, checked , None),
            #boxImageScale = 0.15,
            command = self.change_full,
            pos = (-0.1, 0, -0.6)
            )
            
        self.fps_display = DirectCheckButton (text = "FPS display",
            text_font = self.state.font,     
            text_scale = tx_scale,
            text_align = TextNode.ALeft,
            indicatorValue = self.cfg_p.child ('frame-meter').value,
            scale = .08,
            relief = None,
            boxPlacement = 'right',
            boxRelief = None,
            command = self.change_fps,
            pos = (-0.1, 0, -0.75)
            )
            
        self.sha_display = DirectCheckButton (text = "Shaders",
            text_font = self.state.font,     
            text_scale = tx_scale,
            text_align = TextNode.ALeft,            
            indicatorValue = self.cfg_g.child ('shader').value,
            scale = .08,
            relief = None,
            boxPlacement = 'right',
            boxRelief = None,
            command = self.change_shad,
            pos = (-0.1, 0, -0.9)
            )

    def do_enable (self):
        pass
        
    def do_disable (self):
        pass
        
    def do_destroy (self):
        self.res_txt.destroy ()
        self.res_menu.destroy ()
        self.fps_display.destroy ()
        self.full_screen.destroy ()
        self.sha_display.destroy ()
        self.active = False
        
    def change_shad (self, status):
        self.cfg_g.child ('shader').set_value (bool(status))
        
    def change_fps (self, status):
        self.cfg_p.child ('frame-meter').set_value (bool(status))
        
    def change_full (self, status):
        self.cfg_p.child ('fullscreen').set_value (bool(status))
        self.cfg_p.nudge ()
        
    def change_res (self, arg):
        i = self.sizes_tx.index(arg)
        self.cfg_p.child ('width').set_value (self.sizes[i][0])
        self.cfg_p.child ('height').set_value (self.sizes[i][1])
        self.cfg_p.nudge ()