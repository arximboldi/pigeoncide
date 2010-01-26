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

def make_glow (data_dir = './src/core/sha'):
    """
    TODO: data_dir = current module directory?
    """
    
    glow_shader = Shader.load (data_dir + "/glow_shader.sha")

    # create the glow buffer. This buffer renders like a normal scene,
    # except that only the glowing materials should show up nonblack.
    glow_buffer = base.win.makeTextureBuffer ("glow_scene", 512, 512)
    glow_buffer.setSort (-3)
    glow_buffer.setClearColor (Vec4 (0, 0, 0, 1))

    # We have to attach a camera to the glow buffer. The glow camera
    # must have the same frustum as the main camera. As long as the aspect
    # ratios match, the rest will take care of itself.    
    glow_camera = base.makeCamera (glow_buffer,
                                   lens = base.cam.node ().getLens ())

    # Tell the glow camera to use the glow shader
    temp_node = NodePath (PandaNode("temp_node"))
    temp_node.setShader (glow_shader)
    glow_camera.node ().setInitialState (temp_node.getState ())

    # set up the pipeline: from glow scene to blur x to blur y to main window.
    blur_xbuffer = make_filter_buffer (glow_buffer, "blur_x", -2,
                                       data_dir + "/x_blur_shader.sha")
    blur_ybuffer = make_filter_buffer (blur_xbuffer, "blur_y", -1,
                                       data_dir + "/y_blur_shader.sha")

    finalcard = blur_ybuffer.getTextureCard ()
    finalcard.setAttrib (ColorBlendAttrib.make (ColorBlendAttrib.MAdd))
    return finalcard
    #finalcard.reparentTo (render2d)

def enable_glow (panda):
    if not hasattr (panda, '_glow_filter'):
        glow = make_glow ()
        glow.reparentTo (panda.base.render2d)
        panda._glow_filter = glow

def disable_glow (panda):
    if hasattr (panda, '_glow_filter'):
        panda._glow_filter.removeNode ()
        del panda._glow_filter
        # TODO: better cleanup of the buffers?


