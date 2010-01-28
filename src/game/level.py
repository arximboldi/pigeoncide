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

from base.util import delayed
from ent.physical import StaticPhysicalEntity
from ent.panda import ModelEntity
from phys import geom

from boy import Boy
from pigeon import Pigeon
from flock import make_random_flock
from loader import LoaderData
from sky import SkyEntity

import random

level_physics_category = 0x0002

class LevelEntity (
    StaticPhysicalEntity,
    ModelEntity):
    pass

class Level (LoaderData):
    
    load_models   = [ 'mesh/boy.egg',
                      'mesh/boy-walk.egg',
                      'mesh/boy-feed.egg',
                      'mesh/boy-hit.egg',
                      'mesh/boy-run.egg',
                      'mesh/stick_arch_sub.x',
                      'mesh/pigeon.x' ]
    
    load_textures = [ 'mesh/boy_texture.png',
                      'mesh/boy_texture-glow.png',
                      'mesh/pigeon.png',
                      'mesh/pigeon-glow.png',
                      'sky/1.png',
                      'sky/2.png',
                      'sky/3.png',
                      'sky/4.png',
                      'sky/5.png',
                      'sky/6.png',
                      'sky/1-glow.png',
                      'sky/2-glow.png',
                      'sky/3-glow.png',
                      'sky/4-glow.png',
                      'sky/5-glow.png',
                      'sky/6-glow.png' ]
    
    load_sounds = [ 'snd/electrocute_medium.wav',
                    'snd/electrocute_short.wav',
                    'snd/electrocute_very_long.wav' ]
    
    load_fonts  = []
    
    music       = 'snd/houmdrak.mp3'
    model       = 'mesh/cloud.x'
    geometry    = 'mesh/cloud.x'
    offset      = Vec3 (0, 0, 0)
    sky         = 'sky/boxsky.egg'
    sky_scale   = 1000.
    spawn_spots = [ (Vec3 (0, 70, 20), 0) ]
    flocks_def  = [ 20 ]
    max_time    = 60.
    flocks      = []
    
    def setup_entities (self, entities):
        self.setup_level (entities)
        self.setup_sky (entities)
        self.setup_boy (entities)
        self.setup_flocks (entities)                
        self.do_setup_entities (entities)

    def setup_level (self, entities):
        self.level = LevelEntity (entities = entities,
                                  model    = self.model,
                                  geometry = geom.mesh (self.geometry),
                                  category = level_physics_category)
        self.level.position = self.offset

    def setup_sky (self, entities):
        self.sky = SkyEntity (entities = entities, model = self.sky)
        self.sky.scale = Vec3 (self.sky_scale,
                               self.sky_scale,
                               self.sky_scale)

    def setup_boy (self, entities):
        self.boy = Boy (entities = entities)
        boy_pos, boy_angle = random.choice (self.spawn_spots)
        self.boy.position = boy_pos
        self.boy.angle = boy_angle

    def setup_flocks (self, entities):
        boid_cls = delayed (Pigeon) (the_boy = self.boy)
        for x in self.flocks_def:
            self.flocks.append (
                make_random_flock (entities, 20, boid_cls = boid_cls))

    def dispose (self):
        self.do_cleanup ()
    
    def do_setup_entities (self, entities):
        """ Override this """
        self.level.model.setTexture (loader.loadTexture ('sky/south-epo.png'))
        
        plightnode = PointLight ("point light")
        plightnode.setAttenuation (Vec3 (1, 0.0000005, 0.0000001))
        plight = entities.render.attachNewNode (plightnode)
        
        plight.setPos (100, -100, 1000)
        alightnode = AmbientLight ("ambient light")
        alightnode.setColor (Vec4 (0.3, 0.3, 0.3, 3))
        alight = entities.render.attachNewNode (alightnode)

        entities.render.setLight (alight)
        entities.render.setLight (plight)
        

    def do_cleanup (self):
        pass
