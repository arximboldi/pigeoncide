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

from core.state import State

from physical import PhysicalEntityManager
from task import TaskEntityManager
from panda import PandaEntityManager

class GameEntityManager (
    PhysicalEntityManager,   
    PandaEntityManager,
    TaskEntityManager):
    pass

class LightGameEntityManager (
    PandaEntityManager,
    TaskEntityManager):
    pass


class GameState (State):

    def __init__ (self, *a, **k):
        super (GameState, self).__init__ (*a, **k)
        self._entities = GameEntityManager (
            tasks       = self.tasks,
            phys_events = self.events,
            audio3d     = self.manager.panda.audio3d)
    
    @property
    def entities (self):
        return self._entities

    def do_release (self):
        self._entities.dispose ()
        super (GameState, self).do_release ()


class LightGameState (State):

    def __init__ (self, *a, **k):
        super (LightGameState, self).__init__ (*a, **k)
        self._entities = LightGameEntityManager (
            tasks       = self.tasks,
            audio3d     = self.manager.panda.audio3d)
    
    @property
    def entities (self):
        return self._entities

    def do_release (self):
        self._entities.dispose ()
        super (LightGameState, self).do_release ()

