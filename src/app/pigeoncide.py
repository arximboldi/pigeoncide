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

from base.arg_parser import OptionWith
from core.app import PandaApp

from menu.menu import LoadMenu
from game.game import LoadGame


class PigeoncideApp (PandaApp):

    NAME        = "pigeoncide"
    VERSION     = "0.0.0"
    AUTHOR      = "Pigeoncide development team"
    COPYRIGHT   = "(c) 2009 Pigeoncide development team"
    DESCRIPTION = \
"""\
Pigeoncide is a game that leads you to the dreams of an ill-minded child.
"""

    OPTIONS    = PandaApp.OPTIONS + \
"""
Extra options:
  -s, --state <name>   Set the initial state.
"""
    
    def __init__ (self, *a, **k):
        super (PigeoncideApp, self).__init__ (*a, **k)

        self.root_state = 'game'
        
        self.add_state ('menu', LoadMenu)
        self.add_state ('game', LoadGame)
        
    def do_prepare (self, args):
        self._arg_state = OptionWith (str)
        args.add ('s', 'state', self._arg_state)
        
        super (PigeoncideApp, self).do_prepare (args)
        
    def do_execute (self, freeargs):
        if self._arg_state.value:
            self.root_state = self._arg_state.value
                
        super (PigeoncideApp, self).do_execute (freeargs)
