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

from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import *

from core import task

class Credits (object):

    PROGRAMMERS = [  "Juan Pedro Bolivar Puente",
                        "Alberto Villegas Erce"]
                
    ARTISTS = [ "Marc Andre Modrow",
                    "Sari Sariola"]
    
    SOUND = [ "Circ"]
                    
    def __init__ (self, state = None, *a, **k):
        super (Credits, self).__init__ (*a, **k)
        if state:
            self.state = state
        self.active = False
            
    def do_paint (self):
        tx_scale = (0.6, 0.6)
        init = -0.25
        dif = -0.06
        
        self.prog_lab = []
        self.arts_lab = []
        self.mus_lab = [] 

        i = 0
        self.prog_tab = OnscreenText(
            text = 'Programmers',
            font = self.state.font,
            align = TextNode.ALeft,
            pos = (-0.2, init+dif*i),
            scale = 0.05
            )
        for n in self.PROGRAMMERS:
            self.prog_lab.append (OnscreenText(
                text = n,
                font = self.state.font,
                align = TextNode.ALeft,
                pos = (0.4, init+dif*i),
                scale = 0.04
            ))
            i += 1
        
        i += 2
        self.arts_tab = OnscreenText(
            text = 'Artists',
            font = self.state.font,
            align = TextNode.ALeft,
            pos = (-0.2, init+dif*i),
            scale = 0.05
            )
        for n in self.ARTISTS:
            self.arts_lab.append (OnscreenText(
                text = n,
                font = self.state.font,
                align = TextNode.ALeft,
                pos = (0.4, init+dif*i),
                scale = 0.04
            ))
            i += 1
        
        i += 2
        self.mus_tab = OnscreenText(
            text = 'Music by',
            font = self.state.font,
            align = TextNode.ALeft,
            pos = (-0.2, init+dif*i),
            scale = 0.05
            )
        for n in self.SOUND:
            self.mus_lab.append (OnscreenText(
                text = n,
                font = self.state.font,
                align = TextNode.ALeft,
                pos = (0.4, init+dif*i),
                scale = 0.04
            ))
            i += 1
        self.active = True

        return task.wait(0)
    
    def do_destroy (self):
        for n in self.prog_lab:
            n.destroy ()
        for n in self.arts_lab:
            n.destroy ()
        for n in self.mus_lab:
            n.destroy ()
        self.prog_tab.destroy ()
        self.arts_tab.destroy ()
        self.mus_tab.destroy ()
        
        self.active = False

        return task.wait(0)
        
    def do_enable (self):
        pass
        
    def do_disable (self):
        pass