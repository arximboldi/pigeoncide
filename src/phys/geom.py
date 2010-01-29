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

from pandac.PandaModules import *
from base.util import delayed, selflast

ray     = delayed (selflast (OdeRayGeom))
sphere  = delayed (selflast (OdeSphereGeom))
box     = delayed (selflast (OdeBoxGeom))
capsule = delayed (selflast (OdeCappedCylinderGeom))

@delayed
def node (model, space):
    return OdeTriMeshGeom (space, OdeTriMeshData (model, False))

@delayed
def mesh (model, space, scale = Vec3 (1, 1, 1)):
    cg_model = loader.loadModel (model)
    cg_model.setScale (scale)
    return OdeTriMeshGeom (space,
                           OdeTriMeshData (cg_model, False))

