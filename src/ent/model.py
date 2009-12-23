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

from direct.showbase.ShowBase import ShowBase
from entity import Entity

class ModelEntity (Entity):

    def __init__ (self,
                  render = None,
                  model = None,
                  *a, **k):
        super (ModelEntity, self).__init__ (*a, **k)

        self._model = loader.loadModel (model)
        self._model.reparentTo (render)
        
    def set_position (self, pos):
        super (ModelEntity, self).set_position (pos)
        self._model.setPos (*pos)
        
    def set_hpr (self, hpr):
        super (ModelEntity, self).set_hpr (hpr)
        self._model.setHpr (*hpr)

    def dispose (self):
        super (StaticPhysicalEntity, self).dispose ()
        self._model.removeNode ()
