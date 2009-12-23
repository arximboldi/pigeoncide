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

from core.task import Task

class Entity (Task):

    def __init__ (self, *a, **k):
        super (Entity, self).__init__ (*a, **k)
        self._hpr = None
        self._position = None
        
    def set_position (self, pos):
        self._position = pos

    def set_hpr (self, hpr):
        self._hpr = hpr

    def set_scale (self, scale):
        self._scale = scale

    def get_position (self):
        return self._position

    def get_hpr (self):
        return self._hpr

    def get_scale (self):
        return self._scale

    def dispose (self):
        pass

    position = property (get_position, lambda self, x: self.set_position (x))
    hpr      = property (get_hpr,      lambda self, x: self.set_hpr (x))
    scale    = property (get_scale,    lambda self, x: self.set_scale (x))

