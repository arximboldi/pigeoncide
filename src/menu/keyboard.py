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

from base.signal import slot
from core import (patch_messenger, task)
from core.panda_controller import PandaController
from core.input import *
from base.conf import GlobalConf

from game.defaults import *

class Keyboard (object):

    def __init__(self, state = None, *a, **k):
        super (Keyboard, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False
        self.cfg = GlobalConf ().path ('game.player0.keys')
        
        self.keys_txt = {
            'on_move_forward'   : (1, "Forward"),
            'on_move_backward'  : (2, "Backward"),
            'on_strafe_left'    : (3, "Strafe left"),
            'on_strafe_right'   : (4, "Strafe right"),
            'on_steer_left'     : (5, "Steer left"),
            'on_steer_right'    : (6, "Steer right"),
            'on_throw_weapon'   : (7, "Throw weapon"),
            'on_place_stick'    : (8, "Place stick"),
            'on_feed'           : (9, "Feed"),
            'on_jump'           : (10, "Jump"),
            'on_run'            : (11, "Run"),
            'on_hit'            : (12, "Hit")
            }

    def get_key_name (self, event):
        if event is None or event == 'no-event':
            return "?"
        else:
            return event [6:]
    
    def do_paint (self):
        tx_scale = (0.6, 0.6)
        init = -0.15
        dif = -0.06

        self.keys_btn = {}
        self.keys_lab = {}
        
        for func, (i, bt_text) in self.keys_txt.iteritems ():
            self.keys_btn [func] = DirectButton(
                text = bt_text,
                text_font = self.state.font,
                text_scale = tx_scale,
                text_align = TextNode.ARight,
                scale = .1,
                pos = (0.3, 0, init + dif*i),
                relief = None,
                command = lambda func=func: self.det_key (func)
            )
            self.keys_lab [func] = OnscreenText(text = self.get_key_name (
                    self.cfg.child (func).value),
                font = self.state.font,
                align = TextNode.ALeft,
                pos = (0.7, init+dif*i),
                scale = 0.07
            )
            self.cfg.child (func).on_conf_change += (self.on_key_change)
                
        self.info_txt = OnscreenText (text = 'Select action',
                font = self.state.font,
                pos = (0.4, init+dif*13-0.02),
                scale = 0.04
            )
        self.active = True

    def do_enable (self):
        if self.active:
            for n in self.keys_btn.itervalues ():
                n.setProp ('state', DGG.NORMAL)
        
    def do_disable (self):
        if self.active:
            for n in self.keys_btn.itervalues ():
                n.setProp ('state', DGG.DISABLED)
        
    def do_destroy (self):
        for n in self.keys_btn.itervalues ():
            n.destroy ()
        for n in self.keys_lab.itervalues ():
            n.destroy ()
        self.info_txt.destroy()
        self.active = False
        self.on_key_change.disconnect_sources ()
        
    def det_key (self, key):
        # Deactivate all buttons
        self.state.do_disable ()
        self.keys_lab [key].setText ('?')
        self.info_txt.setText ('Click any key to config')
        self.slot = self.state.events.on_any_event.connect (
            lambda ev, *a, **k: self.get_key (ev, key))
                
    def get_key (self, ev, key):
        if is_key_event (ev):
            self.state.do_enable ()
            self.state.events.on_any_event -= self.slot
            for c in self.cfg.childs ():
                if c.value == ev:
                    c.set_value ('no-event')        
            self.cfg.child (key).set_value (ev)

    @slot
    def on_key_change (self, cfg):
        if self.keys_lab [cfg.name]:
            self.keys_lab [cfg.name].setText (self.get_key_name (cfg.value))
            self.info_txt.setText ('Select button')

