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
import physics
import weapon

import random

class LevelEntity (
    StaticPhysicalEntity,
    ModelEntity):
    pass

class Level (LoaderData):
    
    load_models   = [ 'char/boy-anims.egg',
                      'char/boy-walk.egg',
                      'char/boy-feed.egg',
                      'char/boy-hit.egg',
                      'char/boy-run.egg',
                      'char/pigeon-anims.egg',
                      'char/pigeon-walk.egg',
                      'char/pigeon-takeoff.egg',
                      'char/pigeon-land.egg',
                      'char/pigeon-idle.egg',
                      'char/pigeon-fly.egg',
                      'lvl/modelillo.egg',
                      'obj/stick.egg',
                      'obj/stick-hl.egg',
                      'obj/baseball-bat.egg' ]
    
    load_textures = [ 'char/boy.png',
                      'char/boy-glow.png',
                      'char/pigeon.png',
                      'char/pigeon-glow.png',
                      'sky/green-1.png',
                      'sky/green-2.png',
                      'sky/green-3.png',
                      'sky/green-4.png',
                      'sky/green-5.png',
                      'sky/green-6.png',
                      'sky/green-1-glow.png',
                      'sky/green-2-glow.png',
                      'sky/green-3-glow.png',
                      'sky/green-4-glow.png',
                      'sky/green-5-glow.png',
                      'sky/green-6-glow.png',
                      'obj/baseball-bat.png',
                      'obj/baseball-bat-glow.png',
                      'obj/black.png',
                      'obj/stick.png',
                      'obj/stick-hl.png',
                      'obj/stick-glow.png',
                      'obj/stick-hl-glow.png',
                      'hud/pigeon.png',
                      'hud/clock.png' ]
    
    load_sounds = [ 'snd/houmdrak.mp3',
                    'snd/electrocute-medium.wav',
                    'snd/electrocute-short.wav',
                    'snd/electrocute-long.wav' ]
    
    load_fonts  = [ 'font/gilles.ttf',
                    'font/three-hours.ttf',
                    'font/alte-bold.ttf' ]
    
    music       = 'snd/houmdrak.mp3'
    model       = 'lvl/modelillo.egg'
    geometry    = 'lvl/modelillo.egg'
    offset      = Vec3 (0, 0, 0)
    sky         = 'sky/green-sky.egg'
    sky_scale   = 1000.
    spawn_spots = [ (Vec3 (0, 0, 30), 0) ]
    flocks_def  = [ 20 ]
    max_time    = 120.
    max_sticks  = 4
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
                                  category = physics.level_category)
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
        boid_cls = delayed (Pigeon) (boys = [self.boy])
        for x in self.flocks_def:
            self.flocks.append (
                make_random_flock (entities, 20, boid_cls = boid_cls))

    def dispose (self):
        self.do_cleanup ()
    
    def do_setup_entities (self, entities):
        """
        Override this.
        TODO: A nicer way to express the lights and weapons.
        """
        wep0 = weapon.BaseballBat (entities = entities)
        wep0.position = Vec3 (0, 0, 30)
        
        self.level.model.setTexture (loader.loadTexture ('lvl/grass.png'))
        
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
