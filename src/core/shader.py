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

from base.singleton import Singleton

from direct.showbase.ShowBase import ShowBase

from pandac.PandaModules import Filename,Buffer,Shader
from pandac.PandaModules import PandaNode,NodePath
from pandac.PandaModules import ColorBlendAttrib
from pandac.PandaModules import AmbientLight,DirectionalLight
from pandac.PandaModules import TextNode,Point3,Vec4


def make_filter_buffer (srcbuffer, name, sort, prog):
    blur_buffer = base.win.makeTextureBuffer (name, 512, 512)
    blur_buffer.setSort (sort)
    blur_buffer.setClearColor (Vec4 (1, 0, 0, 1))
    blur_camera = base.makeCamera2d (blur_buffer)
    blur_scene = NodePath ("filter_scene")
    blur_camera.node ().setScene (blur_scene)
    shader = Shader.load (prog)
    card = srcbuffer.getTextureCard ()
    card.reparentTo (blur_scene)
    card.setShader (shader)
    return blur_buffer


class GlowFilter (object):

    is_init = False
    
    def make_glow (self, data_dir = './src/core/sha'):
        """
        TODO: data_dir = current module directory?
        """
    
        glow_shader = Shader.load (data_dir + "/glow_shader.sha")
        
        # create the glow buffer. This buffer renders like a normal
        # scene, except that only the glowing materials should show up
        # nonblack.
        glow_buffer = base.win.makeTextureBuffer ("glow_scene", 512, 512)
        glow_buffer.setSort (-3)
        glow_buffer.setClearColor (Vec4 (0, 0, 0, 1))

        # We have to attach a camera to the glow buffer. The glow
        # camera must have the same frustum as the main camera. As
        # long as the aspect ratios match, the rest will take care of
        # itself.
        glow_camera = base.makeCamera (glow_buffer,
                                       lens = base.cam.node ().getLens ())

        # Tell the glow camera to use the glow shader
        temp_node = NodePath (PandaNode("temp_node"))
        temp_node.setShader (glow_shader)
        glow_camera.node ().setInitialState (temp_node.getState ())

        # set up the pipeline: from glow scene to blur x to blur y to
        # main window.
        blur_xbuffer = make_filter_buffer (glow_buffer, "blur_x", -2,
                                           data_dir + "/x_blur_shader.sha")
        blur_ybuffer = make_filter_buffer (blur_xbuffer, "blur_y", -1,
                                           data_dir + "/y_blur_shader.sha")

        final_card = blur_ybuffer.getTextureCard ()
        final_card.setAttrib (ColorBlendAttrib.make (ColorBlendAttrib.MAdd))

        self.glow_camera  = glow_camera
        self.glow_buffer  = glow_buffer
        self.blur_xbuffer = blur_xbuffer
        self.blur_ybuffer = blur_ybuffer
        self.final_card   = final_card

    def destroy_glow (self):
        """ TODO: This doesn't correctly free al resources, but I'm tired. """
        self.final_card.removeNode ()
        self.glow_camera.removeNode ()
        base.graphicsEngine.removeWindow (self.blur_ybuffer)
        base.graphicsEngine.removeWindow (self.blur_xbuffer)
        base.graphicsEngine.removeWindow (self.glow_buffer)
    
    def enable (self, panda):
        if not self.is_init:
            self.make_glow ()
            self.is_init = True
        self.final_card.reparentTo (panda.base.render2d)

    def disable (self):
        if self.is_init:
            self.destroy_glow ()
            self.is_init = False


