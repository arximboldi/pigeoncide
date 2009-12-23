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

from pandac.PandaModules import Vec3
from base.util import bound
from observer import EntityListener

class EntityFollower (EntityListener):

    def __init__ (self, camera = None, *a, **k):
        super (EntityFollower, self).__init__ (*a, **k)
        self._camera = camera
        
    def on_entity_set_position (self, ent, pos):
        self._camera.lookAt (*pos)

        camvec = Vec3 (*pos) - self._camera.getPos ()
        camvec.setZ (0)
        camvec.normalize ()
        camdist = bound (camvec.length (), 5., 10.)
        
        #self._camera.setPos (self._camera.getPos () + camvec * camdist)

