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
from app.sandbox import Sandbox

from direct.showbase.ShowBase import ShowBase

from pandac.PandaModules import (
    PointLight,
    Vec3,
    Vec4,
    NodePath,
    PandaNode,
    LightRampAttrib,
    AmbientLight,
    TextNode
)

from direct.filter.CommonFilters import CommonFilters

from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectButton import *

from pandac.PandaModules import WindowProperties

class Menu (State):

    def setup (self):
        props = WindowProperties()
        props.setCursorHidden(False)
        base.win.requestProperties(props)

        self.events.event ('panda-escape').connect (self.kill)
        
        self.paint_main ()

    def state_update (self, timer):
        #print "Time: ", timer.elapsed, " FPS: ", timer.fps
        #print "Rate: ", timer.frames / timer.elapsed
        pass

    def release (self):
        self.start.destroy()
        self.options.destroy()
        self.credits.destroy()
        self.exit.destroy()
    
    def create_button (self, btext, pos = (0, 0)):
        return DirectButton(text = (btext, btext, btext, ""),
            scale = .1,
            #command = setText,
            frameSize = (-2.7, 2.7, -1, 1),
            frameColor = (254, 0, 0, 1),
            pos = (pos[0], 0, pos[1])
            )

    def paint_main (self):
        self.start = self.create_button ("Start", pos = (0, 0.35))
        self.options = self.create_button ("Options", pos = (0, 0.1))
        self.credits = self.create_button ("Credits", pos = (0, -0.15))
        self.exit = self.create_button ("Exit", pos = (0, -0.4))
        
        self.start["command"] = lambda: self.manager.change_state ('sandbox')
        self.exit["command"] = self.kill
