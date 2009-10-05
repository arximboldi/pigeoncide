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

from core.timer import *
from core.state import *
from core.task import *

from direct.showbase.ShowBase import ShowBase

_log = get_log (__name__)

class PandaApp (AppBase):

    OPTIONS = AppBase.OPTIONS + \
"""
  -F, --fps <value>   Set the running frames per second to value.
"""
    
    def __init__ (self):
        self.root_state = 'root'
        
        self._tasks = TaskGroup ()
        self._states = StateManager ()
        self._timer = Timer ()
        
        self._tasks.add (self._states)
        self._tasks.add (self._panda_task)

        self._base = None
        self._quit = False

    @property
    def timer (self):
        return self._timer

    @property
    def states (self):
        return self._states

    @property
    def tasks (self):
        return self._tasks

    def do_prepare (self, args):
        args.add ('F', 'fps', OptionConf (
            GlobalConf ().get_path ('panda.fps'), int))
    
    def do_execute (self, args):
        self._states.start (self.root_state)
        self._set_defaults ()
        
        _log.info ("Setting up engine...")
        self._base = ShowBase ()
        
        _log.info ("Running main loop...")
        self._timer.reset ()
        self._timer.fps = GlobalConf ().path ('panda.fps').value
        self._timer.loop (self._tasks.update)
    
    def _set_defaults (self):
        cfg = GlobalConf ().child ('panda')
        cfg.child ('fps').default (0)
        
    def _panda_task (self, timer):
        if self._states.current:
            taskMgr.step ()
        else:
            return Task.KILLED
