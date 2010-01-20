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

"""
No longer needed. Implementation not finished.
"""

from ent.physical import StandingPhysicalEntity, StandingPhysicalEntityDecorator
from ent.task import TaskEntity
from ent.panda import ActorEntity, DelegateActorEntity

from pandac.PandaModules import Vec3
import math

crawl_anim = 'run'

class CrawlerEntityBase (TaskEntity):

    crawl_force = 1000000.0
    max_crawl_speed = 120
    max_crawl_speed_sq = max_crawl_speed ** 2

    def do_update (self, timer):
        super (CrawlerEntityBase, self).do_update (timer)
        self.update_crawler (timer)

    def update_crawler (self, timer):
        angle     = self.angle
        direction = Vec3 (-1. * math.sin (angle),
                          -1. * math.cos (angle), 0)
        speed     = self.linear_velocity
        speeddir  = speed * speed.dot (direction)
        sqlen     = speeddir.lengthSquared ()
        
        if sqlen < self.max_crawl_speed_sq:
            self.add_force (direction * self.crawl_force * timer.delta)


class CrawlerEntity (
    CrawlerEntityBase,
    StandingPhysicalEntity,
    ActorEntity):
    pass

class CrawlerEntityDecorator (
    CrawlerEntityBase,
    StandingPhysicalEntityDecorator,
    DelegateActorEntity):
    pass

