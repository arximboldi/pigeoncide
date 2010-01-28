#
#  Copyright (C) 2010 Juan Pedro Bolivar Puente, Alberto Villegas Erce
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

from ent.panda import ModelEntity
from ent.task import TaskEntity

class SkyEntity (TaskEntity, ModelEntity):

    def __init__ (self, camera = None, *a, **k):
        super (SkyEntity, self).__init__ (*a, **k)
        
        if camera == None:
            camera = base.cam
        self.camera = camera

    def do_update (self, timer):
        self.position = self.camera.getPos ()
