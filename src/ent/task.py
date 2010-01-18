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

from core.task import Task, TaskGroup
from entity import Entity, EntityManager


class TaskEntityManager (EntityManager):
    
    def __init__ (self, tasks = None, *a, **k):
        super (TaskEntityManager, self).__init__ (*a, **k)
        if tasks:
            self.tasks = tasks
        else:
            self.tasks = TaskGroup ()


class TaskEntity (Entity, Task):

    def __init__ (self, entities = None, *a, **k):
        super (TaskEntity, self).__init__ (
            entities = entities,
            *a, **k)
        entities.tasks.add (self)
        
    def dispose (self):
        self.kill ()
        super (TaskEntity, self).dispose ()
