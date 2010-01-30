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
from core.panda_controller import PandaController
from base.conf import GlobalConf
from core.input import *

class Keyboard (object):

    def __init__(self, state = None, *a, **k):
        super (Keyboard, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False
        self.cfg = GlobalConf().child ('game')
        
    def do_paint (self):
        #cfg.child ('music-volume').default (self.DEFAULT_MUSIC_VOLUME)
        tx_scale = (0.6, 0.6)
        init = -0.2
        dif = -0.06
        self.keys_txt = [   "Forward",
                            "Backward",
                            "Strafe left",
                            "Strafe right",
                            "Run",
                            "Hit",
                            "Throw weapon",
                            "Place stick"
                    ]
        self.keys_btn = []
        
        for n in self.keys_txt:
            i = self.keys_txt.index (n)
            self.keys_btn.append( DirectButton(
                text = n,
                text_font = self.state.font,
                text_scale = tx_scale,
                scale = .1,
                pos = (0.3, 0, init+dif*i),
                relief = None,
                command = lambda: self.det_key (i)
            ))
        self.box = OnscreenText(text = 'gs',
            font = self.state.font,
            pos = (0.7, -0.2),
            scale = 0.07,
            )
        
        self.active = True

    def do_enable (self):
        if self.active:
            for n in self.keys_btn:
                n.setProp ('state', DGG.NORMAL)
        
    def do_disable (self):
        if self.active:
            for n in self.keys_btn:
                n.setProp ('state', DGG.DISABLED)
        
    def do_destroy (self):
        for n in self.keys_btn:
            n.destroy ()
        self.box.destroy ()
            
        self.active = False
        
    def det_key (self, key):
        # Deactivate all buttons
        self.state.do_disable ()
        self.slot = self.state.events.on_any_event.connect (
            lambda ev, *a, **k: self.get_key (ev, key))
                
    def get_key (self, ev, key):
        if is_key_event (ev):
            self.state.do_enable ()
            self.state.events.on_any_event -= self.slot
            #self.cfg.child ('').value
            self.box.setText('YEAH')
        
#PLAYER_INPUT_MAP = {
#    'on_move_forward'  : 'panda-w',
#    'on_move_backward' : 'panda-s',
#    'on_strafe_left'   : 'panda-a',
#    'on_strafe_right'  : 'panda-d',
#    'on_steer_left'    : 'panda-k',
#    'on_steer_right'   : 'panda-l',
#    'on_jump'          : 'panda-space',
#    'on_run'           : 'panda-c',
#    'on_hit'           : 'panda-e',
#    'on_throw_weapon'  : 'panda-r',
#    'on_place_stick'   : 'panda-q',
#    'on_steer'         : 'panda-mouse-move',
#}
