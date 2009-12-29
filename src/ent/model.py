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
from panda import PandaEntity
from pandac.PandaModules import *
from direct.actor.Actor import Actor


class ModelEntity (PandaEntity):

    def __init__ (self,
                  model = None,
                  anims = {},
                  *a, **k):
        super (ModelEntity, self).__init__ (*a, **k)

        self._model = Actor (model, anims)
        self._model.pprint ()
        self._model.reparentTo (self._node)

    @property
    def model (self):
        return self._model
    
    def set_model_position (self, pos):
        self._model.setPos (pos)

    def get_model_position (self):
        return self._model.getPos ()
        
    def set_model_hpr (self, hpr):
        self._model.setHpr (hpr)

    def get_model_hpr (self):
        return self._model.getHpr ()
        
    def set_model_scale (self, scale):
        self._model.setScale (scale)

    def get_model_scale (self):
        return self._model.getScale ()

    model_position = property (get_model_position, set_model_position)
    model_hpr      = property (get_model_hpr,      set_model_hpr)
    model_scale    = property (get_model_scale,    set_model_scale)

