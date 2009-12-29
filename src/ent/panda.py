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

from entity import Entity
from pandac.PandaModules import *


class PandaEntity (Entity):

    def __init__ (self,
                  render = None,
                  name   = 'entity',
                  *a, **k):
        super (PandaEntity, self).__init__ (*a, **k)
        
        self._node = NodePath (PandaNode ("holder"))
        self._node.reparentTo (render)

    @property
    def node (self):
        return self._node
        
    def set_position (self, pos):
        super (PandaEntity, self).set_position (pos)
        self._node.setPos (pos)
        
    def set_hpr (self, hpr):
        super (PandaEntity, self).set_hpr (hpr)
        self._node.setHpr (hpr)

    def dispose (self):
        super (PandaEntity, self).dispose ()
        self._node.removeNode ()

