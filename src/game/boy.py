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

from ent.observer import ObservableEntity
from ent.model import ModelEntity
from ent.physical import StandingPhysicalEntity
from pandac.PandaModules import Vec3

import phys.geom as geom
import phys.mass as mass

class Boy (ObservableEntity,
           ModelEntity,
           StandingPhysicalEntity):

    #MODEL = '../data/mesh/boy.x'
    #ANIMS = {}
    
    MODEL = '../data/mesh/ralph.egg.pz'
    ANIMS = { 'run'  : '../data/mesh/ralph-run.egg.pz',
              'walk' : '../data/mesh/ralph-walk.egg.pz' }
    
    def __init__ (self, model = MODEL, *a, **k):
        super (Boy, self).__init__ (geometry = geom.capsule (1.0, 7.0),
                                    mass     = mass.capsule (2, 3, 1.0, 7.0),
                                    model    = model,
                                    anims    = self.ANIMS,
                                    *a, **k)

        self.model_position = Vec3 (.0, .0, -5.0)
        self.model.loadAnims (self.ANIMS)
        self.model.pprint ()
        # self.model_position = Vec3 (.0, .0, -4.5)
        # self.model_scale    = Vec3 (-1, -1, -1)
        # self.model_hpr      = Vec3 (180, 0, 180)

        #self._model.setPlayRate (0.1, 'boy.3')
    
# :egg2pg(warning): AnimBundle boy specifies contradictory number of frames.
# :egg2pg(warning): AnimBundle boy specifies contradictory frame rates.
# :egg2pg(warning): AnimBundle boy specifies contradictory number of frames.
# :egg2pg(warning): AnimBundle boy specifies contradictory frame rates.
# :egg2pg(warning): AnimBundle boy specifies contradictory number of frames.
# LOD: lodRoot
#   Part: modelRoot
#   Bundle: CharacterJointBundle boy
#     Anim: boy
#       File: None
#       NumFrames: 17 PlayRate: 1.00
#     Anim: boy.1
#       File: None
#       NumFrames: 9 PlayRate: 1.00
#     Anim: boy.3
#       File: None
#       NumFrames: 30 PlayRate: 1.00
#     Anim: boy.2
#       File: None
#       NumFrames: 11 PlayRate: 1.00
# LOD: lodRoot
#   Part: modelRoot
#   Bundle: CharacterJointBundle boy
#     Anim: boy
#       File: None
#       NumFrames: 1 PlayRate: 1.00

    def walk (self):
        pass

    def run (self):
        pass

    def jump (self):
        pass

    def crouch (self):
        pass

    def feed (self):
        pass

    def hit (self):
        pass

    
