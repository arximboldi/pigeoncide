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

from base.util import *
from weakref import proxy
from error import *
from base.log import *

_log = get_log (__name__)

class TaskError (CoreError):
    pass

class Task (object):

    KILLED  = 0
    RUNNING = 1
    PAUSED  = 2
    
    def __init__ (self, *a, **k):
        super (Task, self).__init__ (*a, **k)
        self._state = Task.RUNNING
        self._next  = []
        self._manager = None

    def do_update (self, timer):
        pass

    def add_next (self, task):
        self._next.append (task)
        return task
    
    def update (self, timer):
        if self._state == Task.RUNNING:
            self.do_update (timer)
        if self._state == Task.KILLED and self._manager:
            for task in self._next:
                self._manager.add (task)
        return self._state
    
    def pause (self):
        if self._state != Task.KILLED:
            self._state = Task.PAUSED

    def resume (self):
        if self._state != Task.KILLED:
            self._state = Task.RUNNING

    def restart (self):
        self._state = Task.RUNNING

    def kill  (self):
        self._state = Task.KILLED
        
    def is_paused (self):
        return self._state == Task.PAUSED

    def is_killed (self):
        return self._state == Task.KILLED

    @property
    def state (self):
        return self._state

    @property
    def parent (self):
        return self._manager
    
    def _set_parent (self, manager):
        if self._manager and manager:
            raise TaskError ("Already attached.")
        self._manager = manager


class FuncTask (Task):

    def __init__ (self, func = None, *a, **k):
        assert func != None
        super (FuncTask, self).__init__ (*a, **k)
        self._set_func (func)
        
    def _set_func (self, func):
        if func.func_code.co_argcount < 1:
            self._orig = func
            self._func = lambda t: func ()
        else:
            self._orig = self._func = func

    def _get_func (self):
        return self._orig
    
    def do_update (self, timer):
        action = self._func (timer)
        if not action or action == Task.KILLED:
            self.kill ()
        elif action == Task.PAUSED:
            self.pause ()

    func = property (_get_func, _set_func)

class TaskGroup (Task):

    def __init__ (self, *tasks):
        Task.__init__ (self)
        self._tasks = []
        for task in tasks:
            self.add (task)
        
    def do_update (self, timer):
        for task in self._tasks:
            task.update (timer)
        self._tasks = remove_if (Task.is_killed, self._tasks)

        if len (self._tasks) == 0:
            self.kill ()
        
    def add (self, task):
        if not isinstance (task, Task):
            if not callable (task):
                raise TaskError ('You can add either tasks or callables.')
            task = FuncTask (func = task)
        self._tasks.append (task)
        return task

    def remove (self, task):
        self._tasks.remove (task)
        task._set_parent (self)

    def find (self, func):
        for task in self._tasks:
            if isinstance (task, FuncTask) and \
               task.func == func:
                return task

    @property
    def count (self):
        return len (self._tasks)
    
