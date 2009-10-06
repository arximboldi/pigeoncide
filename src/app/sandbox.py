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

from base.util import printer
from core.task import Task
from core.state import State

from direct.showbase.ShowBase import ShowBase

from pandac.PandaModules import (
    PointLight,
    Vec3,
    Vec4,
    NodePath,
    PandaNode,
    LightRampAttrib,
    AmbientLight
)

from direct.filter.CommonFilters import CommonFilters


class Sandbox (State):

    def setup (self):
        self.events.connect ('panda-escape', self.kill)

        m = loader.loadModel ('../data/mesh/pigeon.x')
        m.reparentTo(render)
        m.setPos (0, 70, -20)

        plightnode = PointLight("point light")
        plightnode.setAttenuation(Vec3(1,0,0))
        plight = render.attachNewNode(plightnode)
        plight.setPos(30,-50,0)
        alightnode = AmbientLight("ambient light")
        alightnode.setColor(Vec4(0.8,0.8,0.8,1))
        alight = render.attachNewNode(alightnode)
        render.setLight(alight)
        render.setLight(plight)
        
        base.setBackgroundColor (Vec4 (.4, .6, .9, 1))
        
        # light ramp
        tempnode = NodePath(PandaNode("temp-node"))
        tempnode.setAttrib (LightRampAttrib.makeSingleThreshold(0.5, 0.4))
        tempnode.setShaderAuto()
        base.cam.node().setInitialState (tempnode.getState ())

        # ink
        self.separation = 1.1 # Pixels
        self.filters = CommonFilters (base.win, base.cam)
        filterok = self.filters.setCartoonInk (separation=self.separation)
        

    def do_update (self, timer):
        State.do_update (self, timer)
        #print "Time: ", timer.elapsed, " FPS: ", timer.fps
        #print "Rate: ", timer.frames / timer.elapsed

