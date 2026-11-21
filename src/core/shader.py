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

import os

from base.singleton import Singleton
from base.util import IN_BROWSER
from .paths import SHADER_DIR

from direct.showbase.ShowBase import ShowBase

from pandac.PandaModules import Filename,Buffer,Shader,VirtualFileSystem
from pandac.PandaModules import Texture,TextureStage
from pandac.PandaModules import PandaNode,NodePath
from pandac.PandaModules import ColorBlendAttrib
from pandac.PandaModules import AmbientLight,DirectionalLight
from pandac.PandaModules import TextNode,Point3,Vec4


# The shader sources are written in the common subset of desktop GLSL 1.30
# and GLSL ES 3.00 (WebGL 2), so only the version header differs. WebGL 2
# guarantees highp; mediump overflows on the level's light distances.
GLSL_HEADER = ('#version 300 es\nprecision highp float;\n'
               if IN_BROWSER else '#version 130\n')

def load_shader (vertex, fragment):
    vfs = VirtualFileSystem.getGlobalPtr ()
    def read (name):
        path = Filename.fromOsSpecific (os.path.join (SHADER_DIR, name))
        return GLSL_HEADER + vfs.readFile (path, True).decode ()
    return Shader.make (Shader.SL_GLSL, read (vertex), read (fragment))


# Models glow where they have a glow map on this stage, which the glow
# shader reads as its second texture.
GLOW_STAGE = TextureStage ('glow')
GLOW_STAGE.setSort (1)


def make_black_texture ():
    tex = Texture ('black')
    tex.setup2dTexture (1, 1, Texture.TUnsignedByte, Texture.FRgba)
    tex.setRamImage (b'\x00\x00\x00\xff')
    return tex


def make_filter_buffer (srcbuffer, name, sort, shader):
    blur_buffer = base.win.makeTextureBuffer (name, 512, 512)
    blur_buffer.setSort (sort)
    blur_buffer.setClearColor (Vec4 (1, 0, 0, 1))
    blur_camera = base.makeCamera2d (blur_buffer)
    blur_scene = NodePath ("filter_scene")
    blur_camera.node ().setScene (blur_scene)
    card = srcbuffer.getTextureCard ()
    card.reparentTo (blur_scene)
    card.setShader (shader)
    return blur_buffer


class GlowFilter (object):

    is_init = False
    
    def make_glow (self):
        glow_shader = load_shader ('glow.vert', 'glow.frag')
        
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

        # Tell the glow camera to use the glow shader. Models without their
        # own glow map get a black one, since what an unbound sampler reads
        # depends on the shader language and Panda version: black with the
        # original Cg shader, not black with GLSL in 1.10, white later on.
        temp_node = NodePath (PandaNode("temp_node"))
        temp_node.setShader (glow_shader)
        temp_node.setTexture (GLOW_STAGE, make_black_texture ())
        glow_camera.node ().setInitialState (temp_node.getState ())

        # set up the pipeline: from glow scene to blur x to blur y to
        # main window.
        blur_xbuffer = make_filter_buffer (
            glow_buffer, "blur_x", -2, load_shader ('glow.vert', 'x_blur.frag'))
        blur_ybuffer = make_filter_buffer (
            blur_xbuffer, "blur_y", -1, load_shader ('glow.vert', 'y_blur.frag'))

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


