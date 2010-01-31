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
        self.keys_txt = [   ("Forward",     'on_move_forward'),
                            ("Backward",    'on_move_backward'),
                            ("Strafe left", 'on_strafe_left'),
                            ("Strafe right",'on_strafe_right'),
                            ("Steer left",  'on_steer_left'),
                            ("Steer right", 'on_steer_right'),
                            ("Throw weapon",'on_throw_weapon'),
                            ("Place stick", 'on_place_stick'),
                            ("Feed",        'on_feed'),
                            ("Jump",        'on_jump'),
                            ("Run",         'on_run'),
                            ("Hit",         'on_hit')
                        ]
        
    def do_paint (self):
        tx_scale = (0.6, 0.6)
        init = -0.15
        dif = -0.06

        self.keys_btn = []
        self.keys_lab = []
        
        i = 0
        for bt_text, func in self.keys_txt:
            self.keys_btn.append( DirectButton(
                text = bt_text,
                text_font = self.state.font,
                text_scale = tx_scale,
                text_align = TextNode.ARight,
                scale = .1,
                pos = (0.3, 0, init+dif*i),
                relief = None,
                command = lambda i=i: self.det_key (i)
            ))
            self.keys_lab.append (
                OnscreenText(text = self.cfg.child (func).value[6:],
                font = self.state.font,
                align = TextNode.ALeft,
                pos = (0.7, init+dif*i),
                scale = 0.07
            ))
            i += 1
        
        self.info_txt = OnscreenText (text = 'Select button',
                font = self.state.font,
                pos = (0.4, init+dif*i-0.02),
                scale = 0.04
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
        for n in self.keys_lab:
            n.destroy ()
        self.info_txt.destroy()
        self.active = False
        
    def det_key (self, key):
        # Deactivate all buttons
        self.state.do_disable ()
        self.keys_lab[key].setText('_')
        self.info_txt.setText ('Click any key to config')
        self.slot = self.state.events.on_any_event.connect (
            lambda ev, *a, **k: self.get_key (ev, key))
                
    def get_key (self, ev, key):
        if is_key_event (ev):
            self.state.do_enable ()
            self.state.events.on_any_event -= self.slot
            self.cfg.child (self.keys_txt[key][1]).set_value(ev)
            self.keys_lab[key].setText(ev[6:])
            self.info_txt.setText ('Select button')
