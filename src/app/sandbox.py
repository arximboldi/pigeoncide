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
from core.state import State
from base.conf import GlobalConf

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
        self.events.event ('panda-escape').connect (self.kill)

        m = loader.loadModel ('../data/mesh/pigeon.x')
        m.reparentTo(render)
        m.setPos (0, 70, -20)

        m2 = loader.loadModel ('../data/mesh/cloud.x')
        m2.reparentTo(render)
        m2.setPos (0, 0, -100)
        m2.setScale (3, 3, 3)

        def rotate_task (t):
            m.setHpr (t.elapsed * 10, 0, 0)
            return Task.RUNNING
        self.tasks.add (rotate_task)
        
        plightnode = PointLight("point light")
        plightnode.setAttenuation(Vec3(1,0,0))
        plight = render.attachNewNode(plightnode)
        plight.setPos(100, -100, 1000)
        alightnode = AmbientLight("ambient light")
        alightnode.setColor(Vec4(0.4,0.4,0.4,1))
        alight = render.attachNewNode(alightnode)
        render.setLight(alight)
        render.setLight(plight)
        
        base.setBackgroundColor (Vec4 (.4, .6, .9, 1))
        
        # light ramp
        #tempnode1 = NodePath(PandaNode("temp-node1"))
        render.setAttrib (LightRampAttrib.makeDoubleThreshold(0.4, 0.5, 0.5, 0.9))
        #render.setAttrib (LightRampAttrib.makeHdr0())
        #render.setAttrib (LightRampAttrib.makeHdr1())
        #render.setAttrib (LightRampAttrib.makeHdr2())
        render.setShaderAuto()
        #base.cam.node().setInitialState (tempnode1.getState ())

        # ink
        self.separation = 1.3 # Pixels
        self.filters = CommonFilters (base.win, base.cam)
        filterok = self.filters.setCartoonInk (separation=self.separation)

        self.events.event ('panda-f').connect (
            lambda:
            GlobalConf ().path ('panda.frame-meter').set_value (
                not GlobalConf ().path ('panda.frame-meter').value))

    def state_update (self, timer):
        #print "Time: ", timer.elapsed, " FPS: ", timer.fps
        #print "Rate: ", timer.frames / timer.elapsed
        pass

