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

from pandac.PandaModules import Quat
import math

def distance (a, b):
    return (a - b).length ()

def distance_sq (a, b):
    return (a - b).lengthSquared ()

def to_deg (rad):
    return rad * 180. / math.pi

def to_rad (deg):
    return deg / 180. * math.pi

def hpr_to_quat (hpr):
    q = Quat ()
    q.setHpr (hpr)
    return q

def vec_to_hpr (v):
    q = Quat ()
    q.setX (v.getX ())
    q.setY (v.getY ())
    q.setZ (v.getZ ())
    q.setW (v.getW ())
    return q.getHpr ()

def normalized (vec):
    vec.normalize ()
    return vec

def normalize (vec):
    new_vec = vec.__class__ (vec)
    new_vec.normalize ()
    return new_vec
