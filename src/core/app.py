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

from base.log import get_log
from base.app import *

from state import *

from panda_controller import PandaController

_log = get_log (__name__)

class PandaApp (AppBase):

    OPTIONS = AppBase.OPTIONS + \
"""
Display options:
  -F, --fps <value>    Set the update frames per second.
  -f, --fullscreen     Enable fullscreen mode.
  -w, --window         Enable windowed mode.
  -W, --width <value>  Set window width.
  -H, --height <value> Set window height.
  -m, --frame-meter    Show frames per second meter.
  -M, --hide-meter     Hide the frames per second meter.
"""
    
    def __init__ (self):
        self.root_state = 'root'

        self._states = StateManager ()
        self._panda = PandaController ()
        self._panda.tasks.add (self._states)

        self._quit = False

    @property
    def states (self):
        return self._states

    def do_prepare (self, args):
        cfg = GlobalConf ().child ('panda')
        
        args.add ('F', 'fps', OptionConfWith (cfg.child ('fps'), int))
        args.add ('f', 'fullscreen', OptionConfFlag (cfg.child ('fullscreen')))
        args.add ('w', 'window', OptionConfFlag (cfg.child ('fullscreen'), False))
        args.add ('W', 'width', OptionConfWith (cfg.child ('width'), int))
        args.add ('H', 'height', OptionConfWith (cfg.child ('height'), int))
        args.add ('m', 'frame-meter', OptionConfFlag (cfg.child ('frame-meter')))
        args.add ('M', 'hide-meter', OptionConfFlag (cfg.child ('frame-meter'), False))
        
    def do_execute (self, args):
        
        _log.info ("Setting up engine...")
        self._panda.start (self.NAME + ' ' + self.VERSION)
        messenger._patch_add_forwarder (self._states.events)
                
        _log.info ("Running main loop...")
        self._states.start (self.root_state)
        self._panda.loop ()
        
        _log.info ("Quiting... Have a nice day ;)")
        
